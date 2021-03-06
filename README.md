# es-categorizer 
Extracting categories from an arbitrary block of text using Elasticsearch and Wikipedia.

### TODO:

- Get better wiki article results.
    - Adapt according to text size?

### How?

Given some text, [term vectors](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-termvectors.html) and the [OpenNLP Ingest Processor plugin](https://github.com/spinscale/elasticsearch-ingest-opennlp) can be used to extract keywords that exist **only** within that text, which is not suitable for category extraction. What is needed is a dataset that includes indexable content paired with tags, like an encyclopedia:

1. Index Wikipedia. See [this guide](https://www.elastic.co/blog/loading-wikipedia) and *Setup* below.
2. Use a [More Like This Query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-mlt-query.html) to find documents (wiki articles) that match a given text.
3. Gather the wiki categories of the highest scoring documents.
4. Return a general category based on those categories.

### Prerequisite Dependencies

- python 3
- elasticsearch 5.5.2
- [ICU Analysis Plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-icu.html)
- [Wikimedia's Extra Queries and Filters API Extention Plugin](https://github.com/wikimedia/search-extra)
  - Also [referred to](https://www.elastic.co/guide/en/elasticsearch/plugins/current/api.html) as Elasticsearch Trigram Accelerated Regular Expression Filter

If you're using OS X and homebrew:
```bash
brew install python3
brew install elasticsearch
brew services start elasticsearch  # or just "elasticsearch" for foreground execution
elasticsearch-plugin install analysis-icu
elasticsearch-plugin install org.wikimedia.search:extra:5.5.2
```

### Setup

1. Download the [latest dump of the search index](https://dumps.wikimedia.org/other/cirrussearch/current/enwiki-20170925-cirrussearch-content.json.gz).
```
curl -O "https://dumps.wikimedia.org/other/cirrussearch/current/enwiki-20170925-cirrussearch-content.json.gz"
# If the URL is invalid, go to https://dumps.wikimedia.org/other/cirrussearch/current/ to find an alternative
```

2. Install this program's dependencies: `pip install -r requirements.txt`.
    - You should probably do this in a [virtual environment](https://virtualenv.pypa.io/en/stable/).

3. Run `./main.py`.
    - You will be prompted for the path of the file you downloaded in step 1.
    - If you've got limited storage, consider setting `delete` to `True` for `load_chunks()` beforehand.
    - This command is equivalent to:
```
./main.py delete_index
./main.py create_index
./main.py chunk /path/to/dump
./main.py load
```

4. Test wiki category extraction with `./main.py extract "Some text"`.

Sample output for `./main.py extract -s 3 "The Cubs are destroying the Mets right now."`:
```
1) 21.56842 "1969 Chicago Cubs season"
   - Use mdy dates from November 2013
   - Articles with hCards
   - Chicago Cubs seasons
   - 1969 Major League Baseball season
2) 21.366503 "2015 Chicago Cubs season"
   - Use mdy dates from August 2015
   - Articles with hCards
   - 2015 Major League Baseball season
   - 2015 in sports in Illinois
   - Chicago Cubs seasons
3) 21.28783 "2015 National League Championship Series"
   - Pages using deprecated image syntax
   - 2015 Major League Baseball season
   - National League Championship Series
   - Chicago Cubs postseason
   - 2015 in sports in Illinois
   - 21st century in Chicago
   - 2015 in sports in New York City
   - New York Mets postseason
   - October 2015 sports events
```
> NOTE: Results may differ between search index versions.

5. Test general category extraction with `categorize`.

`./main.py categorize "The Cubs are destroying the Mets right now."` should yield `sports`.
