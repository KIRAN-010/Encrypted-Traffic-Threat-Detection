import io
import subprocess
import sys
from pathlib import Path
import joblib
import pytest
from app import create_app
from train_model import FEATURES, train_model

@pytest.fixture
def client():
    return create_app().test_client()

def upload(client, content, name='traffic.csv'):
    return client.post('/predict', data={'file': (io.BytesIO(content.encode()), name)})

def test_fresh_checkout_and_prediction(client):
    assert client.get('/').status_code == 200
    assert client.get('/api/health').json['status'] == 'ok'
    response = upload(client, 'direction,packet_size,inter_arrival_time,label\n1,1200,0.02,0\n-1,800,0.01,1\n')
    assert response.status_code == 200
    assert [r['Threat'] for r in response.json] == [0, 1]
    assert all(0 <= r['malicious_probability'] <= 1 for r in response.json)

@pytest.mark.parametrize('csv', ['', 'wrong\n1\n', 'packet_size,inter_arrival_time,direction\n', 'packet_size,inter_arrival_time,direction\nabc,0,1', 'packet_size,inter_arrival_time,direction\n10,-1,1', 'packet_size,inter_arrival_time,direction\n10,0,0', 'packet_size,inter_arrival_time,direction\n10,NaN,1', 'packet_size,inter_arrival_time,direction\n10,inf,1', 'packet_size,inter_arrival_time,direction\n0,0,1'])
def test_invalid_csv_returns_validation_error(client, csv):
    r = upload(client, csv)
    assert r.status_code == 400
    assert r.json['error']

def test_missing_wrong_type_oversized(client):
    assert client.post('/predict').status_code == 400
    assert upload(client, 'abc', 'x.txt').status_code == 400
    assert upload(client, 'a' * (2 * 1024 * 1024)).status_code == 413

def test_row_limit(client):
    assert upload(client, 'packet_size,inter_arrival_time,direction\n' + '10,0,1\n' * 10001).status_code == 400

def test_training_reproducible_and_cli_independent_of_cwd(tmp_path):
    p = tmp_path / 'model.pkl'
    model = train_model(output_path=p)
    assert list(joblib.load(p).feature_names_in_) == FEATURES
    script = Path(__file__).resolve().parents[1] / 'train_model.py'
    result = subprocess.run([sys.executable, str(script), '--output', str(p)], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert model.random_state == 42


def test_corrupted_local_model_recovers_without_crashing(tmp_path, monkeypatch):
    import train_model as training
    path = tmp_path / 'bad.pkl'
    path.write_bytes(b'not a pickle')
    monkeypatch.setattr(training, 'MODEL_PATH', path)
    assert set(training.load_or_train().classes_) == {0, 1}
