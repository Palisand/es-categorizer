#!/usr/bin/env python
"""
Extract categories from text using elasticsearch.

Usage:
  main.py create_index
"""
import os
import gzip
import json
# progressbar
# from docopt import docopt
from elasticsearch import Elasticsearch

es = Elasticsearch()
INDEX_NAME = "enwiki"


def create_index():

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
                    if num_line < line_chunksize:
                        num_line += 1
                        fp_chunk.write(line)
                    else:
                        break
                else:
                    break
            print("chunks: {}".format(num_chunk + 1))
            print("\x1b[1A\x1b[2K", end='')
            num_chunk += 1
        print("chunks: {}".format(num_chunk + 1))


def load_chunks():
    pass


def get_categories_for_text(text):
    es.search(
        index=INDEX_NAME,
        doc_type="page",
        body={
            "query": {
                "more_like_this": {
                    "fields": [
                        "content"
                    ],
                    "like": text,
                    # "min_term_freq": 1,
                    # "max_query_terms": 20,
                }
            }
        },
        # _source="categories"  # try list
        # filter_path=["hits.hits._source"]
    )


def setup():
    """
    Build it, chunk it, load it.
    """
    create_index()
    while True:
        dump = input("path to search index dump: ")
        if os.path.exists(dump):
            break
        print("File not found. Try again.")
    chunk_gzipped_file(dump, INDEX_NAME)
    # load_chunks()


def main():
    setup()

    # docopt

    # chunk_wikipedia("/Users/palisand/Desktop/enwiki-20170904-cirrussearch-content.json.gz")

    # with open("fixtures.txt") as fp:
    #     for line in fp:
    #         print(get_categories_for_text(line))


if __name__ == "__main__":
    main()
