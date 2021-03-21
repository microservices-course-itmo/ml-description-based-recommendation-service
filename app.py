import os
from threading import Thread

from flask import Flask, jsonify, request
import traceback
import json

from kafka import KafkaConsumer

from model.model import ModelLoader
from data.db import load_by_ids, drop_table, load_catalogue
from flasgger import Swagger
from flasgger.utils import swag_from
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler


def retrain():
    try:
        # drop_table('wines')
        # load_catalogue()
        start_time = time.time()
        ModelLoader(True).load()
        print("Model retrained in " + str(round(time.time() - start_time, 2)) + " seconds")
    except:
        print("Retraining failed :(")


scheduler = BackgroundScheduler()
scheduler.add_job(retrain, 'date', run_date=(datetime.now() + timedelta(seconds=40)))
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

template = dict(swaggerUiPrefix='/ml-description-based-recommendation-service')
swagger = Swagger(app, template=template)

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


def kafkaListener():
    consumer = KafkaConsumer("eventTopic", auto_offset_reset='earliest', bootstrap_servers=[f'{os.environ["KAFKA_HOST"]}:29092'],
                             api_version=(0, 10),
                             consumer_timeout_ms=1000,
                             value_deserializer=lambda x: x.decode('utf-8'))
    while True:
        time.sleep(60)
        for msg in consumer:
            print("Hello, Kafka!")
            print(msg.value)


if __name__ == "__main__":
    thread = Thread(target=kafkaListener)
    thread.start()
    app.run()