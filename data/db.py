import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
import os

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://os.environ.get('S_POSTGRES_USER'):os.environ.get('S_POSTGRES_PASSWORD')@os.environ.get('S_POSTGRES_HOST'):5432/os.environ.get('S_POSTGRES_DB')"

# db = SQLAlchemy(app)
engine = create_engine('postgresql://ml_service:ml_pass@ml_service_db:5432/ml_service_db', echo=True)
migrate = Migrate(app, engine)


def load_all():
    df = pd.read_sql(f'SELECT * FROM wines', engine)
    df['description'] = df['aroma'] + ' ' + df['taste'] + ' ' + df['description']
    return df


def load_by_ids(ids):
    indices = tuple(ids)
    alcohol = pd.read_sql(f'SELECT id, name, type, crop_year, manufacturer, brand, volume, country, region, color, grape, sugar FROM wines WHERE id IN {indices}', engine)
    return alcohol
