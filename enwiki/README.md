### Index Configuration

https://www.mediawiki.org/wiki/API:Search_and_discovery#CirrusSearch

#### settings.json
https://en.wikipedia.org/w/api.php?action=cirrus-settings-dump&format=json&formatversion=2
```
{
    analysis: .content.page.index.analysis,
    similarity: .contet.page.index.similarity,
    number_of_shards: 1,
    number_of_replicas: 0,
}
```

#### mapping.json
https://en.wikipedia.org/w/api.php?action=cirrus-mapping-dump&format=json&formatversion=2
```
{
    .content
}
```