from flask import Flask, jsonify, request
import traceback
import json
from model.model import ModelLoader
from data.db import load_by_ids

app = Flask(__name__, template_folder='templates')


@app.route('/predict', methods=['GET', 'POST'])
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

    if request.method == 'POST':
        return "Page post"


@app.route('/train', methods=['POST'])
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
