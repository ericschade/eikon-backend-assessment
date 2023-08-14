import os


def trigger_etl():
    print("Triggering ETL...")
    os.system('curl -X POST http://localhost:5000/trigger_etl')


if __name__ == "__main__":
    trigger_etl()