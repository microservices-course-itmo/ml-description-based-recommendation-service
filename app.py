from datetime import datetime, timedelta

from flask import Flask, jsonify, request
import traceback
import json

from kafka_listener.catalog_consumer import get_message_new_wine

from model.model import ModelLoader
from data.db import drop_table, load_catalogue
from flasgger import Swagger
from flasgger.utils import swag_from
import time
from apscheduler.schedulers.background import BackgroundScheduler


def retrain(positions=0):
    try:
        drop_table('wines')
        if positions != 0:
            load_catalogue(positions)
        else:
            load_catalogue()
        start_time = time.time()
        ModelLoader(True).load()
        print("Model retrained in " + str(round(time.time() - start_time, 2)) + " seconds", flush=True)
        f = open('logs.txt', 'a')
        f.write("Model retrained in " + str(round(time.time() - start_time, 2)) + " seconds \n")
        f.close()
    except Exception as e:
        print("Retraining failed :(", flush=True)
        print('ERROR', str(e), flush=True)


scheduler = BackgroundScheduler()
scheduler.add_job(retrain, 'date', run_date=(datetime.now() + timedelta(seconds=30)))
scheduler.add_job(retrain, 'interval', days=1)
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

template = dict(swaggerUiPrefix='/ml-description-based-recommendation-service')
swagger = Swagger(app, template=template)


@app.route('/retrain', methods=['POST'])
def retrain_catalog():
    if request.method == 'POST':
        n = int(request.args['n'])
        scheduler.add_job(lambda: retrain(n), 'date', run_date=(datetime.now() + timedelta(seconds=5)))
        return "Model started retrain"
    else:
        return jsonify({
            "trace": traceback.format_exc()
        })


@app.route('/swagger.json', methods=['GET'])
def returnSwagger():
    with open('swagger.json', 'r', encoding='utf-8') as f:
        text = json.load(f)
    return jsonify(text)


@app.route('/logs', methods=['GET'])
def returnLogs():
    f = open('logs.txt', 'r')
    return str(f.readlines())


@app.route('/predict', methods=['GET'])
@swag_from("swagger/swagger_config_predict.yml")
def predict():
    if request.method == 'GET':
        try:
            model = ModelLoader().load()

            if 'id' in request.args:
                wine_id = request.args['id']
            else:
                return "Error: No wine_id field provided. Please specify the wine_id."

            k = int(request.args['k']) if 'k' in request.args else 10
            desc = request.args['description'] if 'description' in request.args else ''

            indices = model.k_neighbors(wine_id, k + 1, desc)
            result = indices.flatten().tolist()
            response = json.dumps(result, ensure_ascii=False)
            return response
        except:
            return jsonify({
                "trace": traceback.format_exc()
            })


if __name__ == "__main__":
    get_message_new_wine()
    app.run()
