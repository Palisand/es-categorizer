# es-categorizer 
Extracting categories from an arbitrary block of text using elasticsearch.

### How?

Given some text, [term vectors](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-termvectors.html) and the [OpenNLP Ingest Processor plugin](https://github.com/spinscale/elasticsearch-ingest-opennlp) can be used to extract keywords that exist **only** within that text, which is not suitable for category extraction. What is needed is a dataset that includes indexable content paired with tags, like an encyclopedia:

1. Index Wikipedia. See [this guide](https://www.elastic.co/blog/loading-wikipedia).
    1. Download the [latest dump of the search index](https://dumps.wikimedia.org/other/cirrussearch/current/enwiki-20170904-cirrussearch-content.json.gz).
    2. 
2. Use a [More Like This Query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-mlt-query.html) to find documents (wiki articles) that match a given text.
3. Return the categories of the highest scoring documents.

### Prerequisite Dependencies

- elasticsearch 5.5.2
- [ICU Analysis Plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-icu.html)
- [Wikimedia's Extra Queries and Filters API Extention Plugin](https://github.com/wikimedia/search-extra)
  - Also [referred to](https://www.elastic.co/guide/en/elasticsearch/plugins/current/api.html) as Elasticsearch Trigram Accelerated Regular Expression Filter

If you're using OS X and homebrew:
```bash
brew install elasticsearch
brew services start elasticsearch  # or just "elasticsearch" for foreground execution
elasticsearch-plugin install analysis-icu
elasticsearch-plugin install org.wikimedia.search:extra:5.5.2
```