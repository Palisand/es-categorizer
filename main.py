#!/usr/bin/env python

from elasticsearch import Elasticsearch
es = Elasticsearch()

INDEX_NAME = "wikipedia"
DOC_TYPE = "article"


def create_index():
    es.indices.create(
        index=INDEX_NAME,
        body={
            # "settings": {
            #     "number_of_shards": 1  # how much to handle all of wikipedia?
            # },
            "mappings": {
                DOC_TYPE: {
                    "properties": {
                        "content": {
                            "type": "text",
                            "analyzer": "english",
                        },
                        "categories": {
                            "type": "keyword"
                        }
                    }
                }
            }
        },
        ignore=400,
    )


def get_categories_for_text(text):
    es.search(
        index=INDEX_NAME,
        doc_type=DOC_TYPE,
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


def main():
    create_index()
    with open("fixtures.txt") as fp:
        for line in fp:
            print(get_categories_for_text(line))


if __name__ == "__main__":
    main()
