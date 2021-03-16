import pandas as pd
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
engine = create_engine('postgresql://ml_service:ml_pass@postgres:5432/ml_service_db', echo=True)
migrate = Migrate(app, engine)

fields = "description"


def drop_table(table_name):
   base = declarative_base()
   metadata = MetaData(engine, reflect=True)
   table = metadata.tables.get(table_name)
   if table is not None:
       base.metadata.drop_all(engine, [table], checkfirst=True)


def load_catalogue():
    catalogue = create_engine("postgresql://catalog_service_reader:readonly@77.234.215.138:18095/catalog_service_db")
    df = pd.read_sql(f"select wine_id, {fields} from wine_position order by wine_id limit 1000", catalogue)
    print(f'Loaded {df.shape[0]} records from catalogue')
    df.to_sql("wines", engine)


def load_all():
    df = pd.read_sql(f'SELECT wine_id, {fields} FROM wines order by wine_id', engine)
    # df['description'] = df[fields.split(', ')].agg(' '.join, axis=1)
    return df


def load_by_ids(ids):
    indices = tuple(ids)
    alcohol = pd.read_sql(f'SELECT wine_id, {fields} FROM wines WHERE wine_id IN {indices}', engine)
    return alcohol
