import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ml_service:ml_pass@postgres:5432/ml_service_db"

# db = SQLAlchemy(app)
engine = create_engine('postgresql://ml_service:ml_pass@postgres:5432/ml_service_db', echo=True)
migrate = Migrate(app, engine)


def load_all():
    df = pd.read_sql(f'SELECT * FROM wines', app.config['SQLALCHEMY_DATABASE_URI'])
    df['description'] = df['aroma'] + ' ' + df['taste'] + ' ' + df['description']
    return df


def load_by_ids(ids):
    indices = tuple(ids)
    alcohol = pd.read_sql(f'SELECT id, name, type, crop_year, manufacturer, brand, volume, country, region, color, grape, sugar FROM wines WHERE id IN {indices}', engine)
    return alcohol
