from flask import Flask, jsonify, request
import traceback
import json
from model.model import ModelLoader
from data.db import load_by_ids, drop_table, load_catalogue
from flasgger import Swagger
from flasgger.utils import swag_from
import time
from apscheduler.schedulers.background import BackgroundScheduler


def retrain():
    try:
        drop_table('wines')
        load_catalogue()
        start_time = time.time()
        ModelLoader(True).load()
        print("Model retrained in " + str(round(time.time() - start_time, 2)) + " seconds")
    except:
        print("Retraining failed :(")


scheduler = BackgroundScheduler()
scheduler.add_job(retrain, 'interval', minutes=720)
scheduler.start()

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

app.config["SWAGGER"] = {
    "title": "ML-description-based-recommendation",
    "uiversion": 3,
    "static_folder": "static",
    "specs_route": "/swagger/",
    "static_url_path": "/ml-description-based-recommendation-service/static",  # server settings
    # "static_url_path": "/static",  # local settings
    "specs": [
        {
            "endpoint": 'swagger',
            "route": '/ml-description-based-recommendation-service/swagger.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    'openapi': '3.0.2',
}

swagger = Swagger(app)


@app.route('/swagger.json', methods=['GET'])
def returnSwagger():
    with open('swagger.json', 'r', encoding='utf-8') as f:
        text = json.load(f)
    return jsonify(text)


@app.route('/predict', methods=['GET'])
@swag_from("swagger/swagger_config_predict.yml")
def predict():
    if request.method == 'GET':
        try:
            model = ModelLoader().load()

            if 'wine_id' in request.args:
                wine_id = request.args['wine_id']
            else:
                return "Error: No wine_id field provided. Please specify an wine_id."

            k = int(request.args['k']) if 'k' in request.args else 10
            desc = request.args['description'] if 'description' in request.args else ''

            indices = model.k_neighbors(wine_id, k + 1, desc)
            indices = indices.flatten()
            prediction = load_by_ids(indices)
            result = prediction.to_json(orient="index")
            parsed = json.loads(result)
            response = json.dumps(parsed, ensure_ascii=False)
            return response
        except:
            return jsonify({
                "trace": traceback.format_exc()
            })


# @app.route('/retrain', methods=['POST'])
# @swag_from("swagger/swagger_config_retrain.yml")
# def train():
#     if request.method == 'POST':
#         try:
#             start_time = time.time()
#             ModelLoader(True).load()
#             return "model retrained in " + str(round(time.time() - start_time, 2)) + " seconds"
#         except:
#             return jsonify({
#                 "trace": traceback.format_exc()
#             })


if __name__ == "__main__":
    app.run()
