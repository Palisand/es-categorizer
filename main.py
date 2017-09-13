#!/usr/bin/env python
"""
Extract categories from text using Elasticsearch and Wikipedia.

Usage:
  main.py
  main.py create_index
  main.py delete_index
  main.py chunk <filepath>
  main.py load [-d | --delete]
  main.py extract [-s <int> | --size=<int>] <text>
  main.py (-h | --help)

Options:
 -h --help              Show this screen.
 -d --delete            Delete chunk-files after loading them.
 -s <int> --size=<int>  Result set size [default: 5].

"""
import os
import sys
import gzip
import json
import subprocess
from docopt import docopt
from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk
try:
    import progressbar
    MOCK_PROGRESSBAR = False
except ImportError:
    MOCK_PROGRESSBAR = True

es = Elasticsearch()
INDEX_NAME = "enwiki"


class MockProgressBar(object):
    """
    Mock progressbar.ProgressBar
    (Used if progressbar2 is not installed.)
    """
    def __init__(self, max_value):
        self.max_value = max_value

    def update(self, num):
        print('{:.0f}% ({} of {})'.format(
            (num / self.max_value) * 100, num, self.max_value))
        print("\x1b[1A\x1b[2K", end='')

    def finish(self):
        print('100% ({0} of {0})'.format(self.max_value))


def delete_index():
    """ Delete the index if it exists. """
    if es.indices.exists(INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)


def create_index():
    """ Create the index if it doesn't exist. """
    if not es.indices.exists(INDEX_NAME):

        def load_index_config(config):
            with open(os.path.join(INDEX_NAME, "{}.json".format(config))) as fp:
                return json.load(fp)

        es.indices.create(
            index=INDEX_NAME,
            body={
                "settings": load_index_config("settings"),
                "mappings": load_index_config("mapping"),
            },
        )

    else:
        print("index '{}' already exists".format(INDEX_NAME))


def chunk_gzipped_file(filepath, prefix):
    """
    Split the gzipped file associated with the supplied filepath into
    files of up to 500 lines each. The chunk files will consist of
    uncompressed data and will be named with the format "prefix{:04d}"
    and placed in a "chunks" directory.

    Example:

        Given gzipped file with 632 lines (when unzipped) and a prefix
        of "foo", the following files will be created:

        chunks/
        ├── foo0001 (500 lines)
        ├── foo0002 (500 lines)
        └── foo0003 (132 lines)
    """
    chunk_dir = "chunks"
    line_chunksize = 500

    if not os.path.exists(chunk_dir):
        os.mkdir(chunk_dir)

    with gzip.open(filepath, "rb") as fp:
        num_chunk = 0
        while True:
            num_line = 0
            with open(
                os.path.join(chunk_dir, "{}{:04d}".format(prefix, num_chunk)), "wb"
            ) as fp_chunk:
                for line in fp:
                    fp_chunk.write(line)
                    if num_line < line_chunksize - 1:
                        num_line += 1
                    else:
                        break
                else:
                    break
            print("chunks: {}".format(num_chunk + 1))
            print("\x1b[1A\x1b[2K", end='')
            num_chunk += 1
        print("chunks: {}".format(num_chunk + 1))


def load_chunks(prefix, delete=False):

    # FIXME: use bulk / parallel_bulk helper instead of subprocess if possible
    # https://stackoverflow.com/questions/46164822/elasticsearch-py-bulk-helper-equivalent-of-curl-with-file
    #
    # with open("chunks/enwiki000x") as fp:
    #     bulk(
    #         client=es,
    #         index=INDEX_NAME,
    #         actions=fp
    #     )

    chunks = list(filter(lambda c: c.startswith(prefix), os.listdir("chunks")))
    bar = progressbar.ProgressBar if not MOCK_PROGRESSBAR else MockProgressBar
    bar = bar(max_value=len(chunks))

    num_failed_chunks = 0
    for i, chunkname in enumerate(chunks):
        therighteouspathofthechunk = os.path.join("chunks", chunkname)
        try:
            subprocess.check_output([
                "curl",
                "-s",
                "-XPOST",
                "localhost:9200/{}/_bulk".format(INDEX_NAME),
                "--data-binary",
                "@{}".format(therighteouspathofthechunk)
            ])
        except subprocess.CalledProcessError:
            num_failed_chunks += 1
            print("Failed to load {}".format(therighteouspathofthechunk))
        else:
            delete and os.remove(therighteouspathofthechunk)
        bar.update(i + 1)
    bar.finish()

    if num_failed_chunks:
        print("Failed to load {} chunk files.".format(num_failed_chunks))


def get_categories_for_text(text, result_set_size=5):
    result = es.search(
        index=INDEX_NAME,
        doc_type="page",
        body={
            "query": {
                "more_like_this": {
                    "fields": [
                        "text"
                        # "source_text.trigram"
                        # "source_text.plain"
                    ],
                    "like": text,
                    "min_term_freq": 1,
                    "max_query_terms": 25,
                    "min_doc_freq": 5
                }
            }
        },
        size=result_set_size,
        _source=["title", "category"],
        filter_path=["hits.hits._source", "hits.hits._score"]
    )

    # print(json.dumps(result, indent=2))

    if "hits" in result:
        for i, hit in enumerate(result["hits"]["hits"]):
            source = hit["_source"]
            print('\x1b[1m{}) {} "{}"\x1b[0m'.format(i + 1, hit["_score"], source["title"]))
            for category in source["category"]:
                print("   -", category)
    else:
        print("\x1b[31mNo categories found.\x1b[0m")


def setup():
    """
    Wipe it, build it, chunk it, load it.
    """
    delete_index()
    create_index()
    while True:
        dump = input("path to gzipped search index dump: ")
        if os.path.exists(dump):
            break
        print("File not found. Try again.")
    chunk_gzipped_file(dump, INDEX_NAME)
    load_chunks(INDEX_NAME)


def main(argv):
    doc = docopt(__doc__)

    if len(argv) == 1:
        setup()
    else:
        doc["create_index"] and create_index()
        doc["delete_index"] and delete_index()
        doc["chunk"] and chunk_gzipped_file(doc["<filepath>"], INDEX_NAME)
        doc["load"] and load_chunks(INDEX_NAME, doc["--delete"])
        doc["extract"] and get_categories_for_text(doc["<text>"], doc["--size"])


if __name__ == "__main__":
    main(sys.argv)
