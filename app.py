from flask import Flask, jsonify
import flask
import pickle
import pandas as pd
import traceback
import json

app = Flask(__name__, template_folder='templates')

with open('models/knn.pkl', 'rb') as f:
    model, X, y = pickle.load(f)

with open('models/preprocessing.pkl', 'rb') as f:
    wine_review_vectors, winestyle_filtered = pickle.load(f)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/predict/<int:wine_id>', methods=['POST', 'GET'])
def predict(wine_id=None):
    if flask.request.method == 'GET':
        try:
            winestyle_filtered = pd.read_csv('data/winestyle_filtered.csv', index_col='id')
            id_list = list(winestyle_filtered.index.values)
            distances, indices = model.kneighbors(X[id_list.index(wine_id)].reshape(1, -1))
            indices = indices.flatten()
            nearest = y[indices]
            prediction = winestyle_filtered.iloc[nearest]
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
        # try:
        #     json_ = request.json
        #     print(json_)
        #     query_ = pd.get_dummies(pd.DataFrame(json_))
        #     query = query_.reindex(columns=model_columns, fill_value=0)
        #     prediction = list(classifier.predict(query))
        #
        #     return jsonify({
        #         "prediction": str(prediction)
        #     })
        #
        # except:
        #     return jsonify({
        #         "trace": traceback.format_exc()
        #     })


if __name__ == "__main__":
    app.run()
