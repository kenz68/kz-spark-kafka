

## Run docker image

```
    docker pull elasticsearch:8.8.0
    docker run --rm --name elasticsearch_container -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" elasticsearch:8.8.0

```

## Use es-client-docker-compose.yml file to run the elasticsearch container.

```
    docker-compose -f es-client-docker-compose.yml up -d
```

## Create a index

```curl -X PUT http://localhost:9200/products```

## Insert data into the index

```
    curl -X POST -H 'Content-Type: application/json' 
    -d '{ "name": "Awesome T-Shirt", "description": "This is an awesome t-shirt for casual wear.", 
    "price": 19.99, "category": "Clothing", "brand": "Example Brand" }' 
    http://localhost:9200/products/_doc
```

The output should be:
```
    {
        "_index": "products",
        "_id": "M2I6_5IBypxrXonC1TUn",
        "_version": 1,
        "result": "created",
        "_shards": {
            "total": 2,
            "successful": 1,
            "failed": 0
        },
        "_seq_no": 0,
        "_primary_term": 1
    }
```

## Query the data
```
    curl -X GET "localhost:9200/products/_search?pretty" -H 'Content-Type: application/json' 
    -d' { "query": { "match": { "name": "t-shirt" } } }'
```

Output:
```
    {
        "took": 4,
        "timed_out": false,
        "_shards": {
            "total": 1,
            "successful": 1,
            "skipped": 0,
            "failed": 0
        },
        "hits": {
            "total": {
                "value": 1,
                "relation": "eq"
            },
            "max_score": 1.0,
            "hits": [
                {
                    "_index": "products",
                    "_id": "M2I6_5IBypxrXonC1TUn",
                    "_score": 1.0,
                    "_source": {
                        "name": "Awesome T-Shirt",
                        "description": "This is an awesome t-shirt for casual wear.",
                        "price": 19.99,
                        "category": "Clothing",
                        "brand": "Example Brand"
                    }
                }
            ]
        }
    }
```