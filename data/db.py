import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ml_service:ml_pass@localhost:5432/ml_service_db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def load_all():
    df = pd.read_csv('data/alcohol.csv').head(30000)
    df['description'] = df['aroma'] + ' ' + df['taste'] + ' ' + df['description']
    return df


def load_by_ids(ids):
    alcohol = pd.read_csv('data/alcohol30000.csv')
    return alcohol.iloc[ids]
