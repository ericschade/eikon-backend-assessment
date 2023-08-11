import os

SQLALCHEMY_TRACK_MODIFICATIONS = False
if os.environ.get("SQLALCHEMY_DATABASE_URI"):
    # within docker, use the db address that docker-compose.yaml assigns
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
else:
    # for quick iteration outside of docker, the port/address will be different
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://test:test@localhost:5405/test'
