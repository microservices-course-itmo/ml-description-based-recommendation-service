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

app = Flask(__name__)

app.config["SWAGGER"] = {
    "title": "Swagger-UI",
    "uiversion": 3
    # 'openapi': '3.0.2'
    # 'prefix_ids': True
}
# swagger_config = Swagger.DEFAULT_CONFIG
# swagger_config['swagger_ui_bundle_js'] = '//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js'
# swagger_config['swagger_ui_standalone_preset_js'] = '//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js'
# swagger_config['jquery_js'] = '//unpkg.com/jquery@2.2.4/dist/jquery.min.js'
# swagger_config['swagger_ui_css'] = '//unpkg.com/swagger-ui-dist@3/swagger-ui.css'

# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ml_service:ml_pass@postgres:5432/ml_service_db"
# db = SQLAlchemy(app)
# df_db = pd.read_csv('data/alcohol_15000.csv')
# df_db.columns = [c.lower() for c in df_db.columns]
# engine = create_engine('postgresql://ml_service:ml_pass@postgres:5432/ml_service_db', echo=True)
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
    "basePath": "/api",
    "schemes": [
        "http",
        "https"
      ],
    "static_url_path": "/ml-description-based-recommendation-service/static",
    "static_folder": "static",  # must be set by user
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
