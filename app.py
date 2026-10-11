"""Local metadata classifier; the bundled dataset is a demonstration only."""
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge
from train_model import load_or_train, read_features


def create_app(model=None):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    classifier = model if model is not None else load_or_train()

    @app.get('/')
    def home():
        return render_template('index.html')

    @app.get('/api/health')
    def health():
        return jsonify(status='ok', model='RandomForest', mode='demo')

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(_):
        return jsonify(error='Upload is limited to 2 MiB.'), 413

    @app.post('/predict')
    def predict():
        file = request.files.get('file')
        if file is None or not file.filename:
            return jsonify(error='Choose a CSV file using the file field.'), 400
        if not file.filename.lower().endswith('.csv'):
            return jsonify(error='Only CSV files are supported.'), 400
        try:
            features = read_features(file.stream)
        except (ValueError, UnicodeError) as exc:
            return jsonify(error=str(exc)), 400
        predictions = classifier.predict(features)
        probabilities = classifier.predict_proba(features)
        malicious_index = list(classifier.classes_).index(1)
        features['Threat'] = predictions.astype(int)
        features['malicious_probability'] = probabilities[:, malicious_index].round(4)
        return jsonify(features.to_dict(orient='records'))

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
