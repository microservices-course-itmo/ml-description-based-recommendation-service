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

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

app.config["SWAGGER"] = {
    "title": "Swagger-UI",
    "uiversion": 3,
    "static_folder": "static",
    "specs_route": "/swagger/",
    "static_url_path": "/ml-description-based-recommendation-service/static",
    # "static_url_path": "/static",
    "specs": [
        {
            "endpoint": 'swagger',
            "route": '/ml-description-based-recommendation-service/swagger.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    'openapi': '3.0.2'
    # 'prefix_ids': True
}

swagger = Swagger(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ml_service:ml_pass@postgres:5432/ml_service_db"
# db = SQLAlchemy(app)
# df_db = pd.read_csv('data/alcohol_15000.csv')
# df_db.columns = [c.lower() for c in df_db.columns]
# engine = create_engine('postgresql://ml_service:ml_pass@postgres:5432/ml_service_db', echo=True)
# df_db.to_sql("wines", engine)


@app.route('/predict', methods=['GET'])
@swag_from("swagger/swagger_config_predict.yml", validation=True)
def predict():
    if request.method == 'GET':
        try:
            model = ModelLoader().load()

            if 'wine_id' in request.args:
                wine_id = int(request.args['wine_id'])
            else:
                return "Error: No wine_id field provided. Please specify an wine_id."

            k = int(request.args['k']) if 'k' in request.args else 10
            desc = request.args['description'] if 'description' in request.args else ''

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
@swag_from("swagger/swagger_config_retrain.yml", validation=True)
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
