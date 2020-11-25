from flask import Flask, jsonify
import flask
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
            print(indices)
            prediction = load_by_ids(indices)
            print(prediction[['id', 'color', 'sugar']])
            # to do drop
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
