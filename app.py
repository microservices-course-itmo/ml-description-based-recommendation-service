from flask import Flask, jsonify, request
import traceback
import json
from model.model import ModelLoader
from data.db import load_by_ids
import pandas as pd
from flasgger import Swagger
from flasgger.utils import swag_from
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import os

app = Flask(__name__, template_folder='templates')
app.config["SWAGGER"] = {"title": "Swagger-UI", "uiversion": 2}

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://os.environ.get('S_POSTGRES_USER'):os.environ.get('S_POSTGRES_PASSWORD')@os.environ.get('S_POSTGRES_HOST'):5432/os.environ.get('S_POSTGRES_DB')"
db = SQLAlchemy(app)
df_db = pd.read_csv('data/alcohol_15000.csv')
df_db.columns = [c.lower() for c in df_db.columns]
df_db.to_sql("wines", app.config['SQLALCHEMY_DATABASE_URI'])
# engine = create_engine('postgresql://ml_service:ml_pass@db:5432/ml_service_db', echo=True)
# df_db.to_sql("wines", engine)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "predict",
            "route": "/ml-description-based-recommendation-service",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True
        }
    ],
    "static_url_path": "/flagger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}

swagger = Swagger(app, config=swagger_config)


@app.route('/predict', methods=['GET'])
@swag_from("swagger/swagger_config_predict.yml")
def predict():
    if request.method == 'GET':
        try:
            model = ModelLoader().load()
            args = request.args
            wine_id, k = map(int, (args['wine_id'], args['k']))
            desc = args['description']
            indices = model.k_neighbors(wine_id, k, desc)
            indices = indices.flatten()
            prediction = load_by_ids(indices)
            # print(prediction[['id', 'color', 'sugar']])
            result = prediction.to_json(orient="index")
            parsed = json.loads(result)
            response = json.dumps(parsed, ensure_ascii=False)
            return response
        except:
            return jsonify({
                "trace": traceback.format_exc()
            })


@app.route('/retrain', methods=['POST'])
@swag_from("swagger/swagger_config_retrain.yml")
def train():
    if request.method == 'POST':
        try:
            ModelLoader(True).load()
            return "model retrain"
        except:
            return jsonify({
                "trace": traceback.format_exc()
            })


if __name__ == "__main__":
    app.run()
