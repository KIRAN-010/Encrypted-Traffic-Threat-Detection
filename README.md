# Encrypted Traffic Threat Detection

A working local Flask web app that classifies traffic metadata with a reproducible Random Forest model. It analyzes packet size, inter-arrival time and direction without reading decrypted payloads.

The bundled dataset has **four demonstration rows**. The app is suitable for demonstrating an upload-to-prediction pipeline, but this dataset cannot establish accuracy, false-positive rates or generalization to real attacks. Model probabilities are not calibrated threat confidence.

## Run

Python 3.10+:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. A fresh checkout trains the demo classifier in memory on startup, so no missing model file or manual training step blocks the interface. Paths are resolved relative to the source files.

To run alongside TruthLens on a different port:

```bash
python -m flask --app app run --host 127.0.0.1 --port 5001
```

## CSV format

```csv
packet_size,inter_arrival_time,direction
1200,0.02,1
800,0.01,-1
```

- `packet_size`: 1–65,535 bytes.
- `inter_arrival_time`: nonnegative seconds.
- `direction`: `-1` or `1` using a consistent traffic-direction convention.
- An optional `label` column is ignored during prediction; feature column order does not matter.
- Upload limits: 2 MiB and 10,000 records. Missing columns, nonnumeric values, NaN, infinity and unexpected columns return useful JSON validation errors.

The page displays predictions and allows downloading the complete JSON result. The table displays the first 200 records.

## Train on your own data

Add `label`, where 0 = benign and 1 = malicious. Both classes are required.

```bash
python train_model.py --data /path/to/labeled-traffic.csv
```

This writes `rf_model.pkl`, which the app loads on its next startup. Only load model files you created or trust: pickle-based model artifacts can execute code. Retrain after changing scikit-learn versions. The model uses a fixed random seed; evaluate with independent, representative traffic before operational use.

## API and tests

- `GET /api/health`: startup health.
- `POST /predict`: multipart form upload in the `file` field; returns a JSON array containing metadata, `Threat` (0/1), and `malicious_probability`.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

GitHub Actions checks Python 3.10 and 3.12. Tests cover fresh-start prediction, training, column order, input validation and upload limits.

Original project attribution: Yogi-TechoMass.
