import pandas as pd
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
engine = create_engine('postgresql://ml_service:ml_pass@postgres:5432/ml_service_db')
# catalogue = create_engine("postgresql://catalog_service_reader:readonly@77.234.215.138:18095/catalog_service_db")
catalogue = create_engine("postgresql://catalog_service_reader:readonly@postgres:5432/catalog_service_db",)

migrate = Migrate(app, engine)

fields = "description"


def drop_table(table_name):
   base = declarative_base()
   metadata = MetaData(engine, reflect=True)
   table = metadata.tables.get(table_name)
   if table is not None:
       base.metadata.drop_all(engine, [table], checkfirst=True)


def load_catalogue(lim=0):
    if lim:
        df = pd.read_sql(f"select id, {fields} from wine_position order by id limit {lim}", catalogue)
    else:
        df = pd.read_sql(f"select id, {fields} from wine_position order by id", catalogue)
    f = open('../logs.txt', 'a')
    print(f'Loaded {df.shape[0]} records from catalogue', flush=True)
    f.write('Loaded ' + str(df.shape[0]) + ' records from catalogue \n')
    f.close()
    df.to_sql("wines", engine, index=False)


def load_all():
    df = pd.read_sql(f'SELECT id, {fields} FROM wines order by id', engine)
    # df['description'] = df[fields.split(', ')].agg(' '.join, axis=1)
    # df['description'] = ' '.join([df[field] for field in fields.split(', ')])
    return df


def load_by_ids(ids):
    indices = tuple(ids)
    alcohol = pd.read_sql(f'SELECT id, {fields} FROM wines WHERE id IN {indices}', engine)
    return alcohol


def add_new_wine(new_wine_id, new_wine_description):
    engine.connect().execute(f"INSERT INTO wines (id, description) VALUES ({new_wine_id}, {new_wine_description});")
    print(f'Received one new wine with parameters: {new_wine_id}, {new_wine_description}', flush=True)
    f = open('../logs.txt', 'a')
    f.write(f'Received one new wine with parameters: {new_wine_id}, {new_wine_description} \n')
    f.close()
