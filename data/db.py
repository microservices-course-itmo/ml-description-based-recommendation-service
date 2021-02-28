import pandas as pd
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import create_engine

app = Flask(__name__)
engine = create_engine('postgresql://ml_service:ml_pass@postgress:5432/ml_service_db', echo=True)
migrate = Migrate(app, engine)


def load_catalogue():
    catalogue = create_engine("postgresql://catalog_service_reader:readonly@77.234.215.138:18095/catalog_service_db")
    fields = "id, description"
    df = pd.read_sql(f"select {fields} from wine_position", catalogue)
    df.to_sql("wines", engine)


def load_all():
    df = pd.read_sql(f'SELECT * FROM wines', engine)
    df['description'] = df['aroma'] + ' ' + df['taste'] + ' ' + df['description']
    return df


def load_by_ids(ids):
    indices = tuple(ids)
    alcohol = pd.read_sql(f'SELECT id, name, type, crop_year, manufacturer, brand, volume, country, region, color, grape, sugar FROM wines WHERE id IN {indices}', engine)
    return alcohol
