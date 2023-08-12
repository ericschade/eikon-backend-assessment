
### Requirements
- Python 3.7+
- Docker
- PostgreSQL

Building and running the service from the command line:

```
docker compose up
```


To trigger an etl:

```commandline
curl -X POST -H "Content-Type: application/json" -d "{\"label\": \"etl_run_label\"}" http://localhost:5000/trigger_etl
```
double quotes are escaped for windows cmd line

To get past results:

```commandline
curl http://localhost:5000/etl_results/etl_run_label
```

