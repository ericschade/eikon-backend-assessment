from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

# Init App
app = Flask(__name__)

# Database config
app.config.from_object('config')

# Init db
db = SQLAlchemy(app)
# Init Marshmallow
ma = Marshmallow(app)

from routes import *
from model import *

# build db
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()
    db.session.commit()


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
