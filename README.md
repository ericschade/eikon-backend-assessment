
### Requirements
- Python 3.7+
- Docker
- PostgreSQL

Building and running the service from the command line:

```
docker compose up
```

BUT you can use the provided python script which will run in detached mode:
```commandline
python scripts/build_and_compose.py
```

To trigger an etl using curl:

```commandline
curl -X POST http://localhost:5000/trigger_etl
```
...but you can also use the provided script:
```commandline
python scripts/trigger_etl.py
```

To get past results with curl:
```commandline
curl http://localhost:5000/etl_results/etl_id
```
or
```commandline
curl http://localhost:5000/etl_results/user_id
```

or using a SQL query:

to get run aggregation...
```
SELECT * from etl_run
```
or user results table...
```
SELECT * from etl_user_results
```

