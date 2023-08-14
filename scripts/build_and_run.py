import os


def compose():
    os.system('echo "Building and running Eikon backend challenge ETL..."')
    os.system("docker compose up -d")
    os.system('echo "Service is running. Try triggering an ETL process with `python scripts/trigger_etl.py`"')


if __name__ == "__main__":
    compose()
