from flask import Flask, jsonify
import flask
import pickle
import pandas as pd
import traceback
import json
from model.model import ModelLoader
from data.db import load_by_ids

model = ModelLoader(True).load()

app = Flask(__name__, template_folder='templates')

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/predict/<int:wine_id>', methods=['POST', 'GET'])
def predict(wine_id=None):
    if flask.request.method == 'GET':
        try:
            distances, indices = model.k_neighbors(wine_id)
            indices = indices.flatten()
            prediction = load_by_ids(indices)
            prediction.drop(index=wine_id, inplace=True)
            result = prediction.to_json(orient="index")
            parsed = json.loads(result)
            response = json.dumps(parsed, ensure_ascii=False)
            return response
        except:
            return jsonify({
                "trace": traceback.format_exc()
            })

    if flask.request.method == 'POST':
        return "Page post"



if __name__ == "__main__":
    app.run()
