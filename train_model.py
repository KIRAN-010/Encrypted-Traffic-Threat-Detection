"""Reproducible training and shared feature validation."""
import argparse
import pickle
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = Path(__file__).resolve().parent
FEATURES = ['packet_size', 'inter_arrival_time', 'direction']
MODEL_PATH = BASE_DIR / 'rf_model.pkl'
DATA_PATH = BASE_DIR / 'traffic_data.csv'


def read_features(source, training=False):
    try:
        frame = pd.read_csv(source, nrows=10001)
    except (pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise ValueError('Provide a nonempty, well-formed CSV file.') from exc
    required = FEATURES + (['label'] if training else [])
    if not set(required).issubset(frame.columns):
        raise ValueError('Required columns: ' + ', '.join(required))
    if set(frame.columns) - set(FEATURES + ['label']):
        raise ValueError('Unexpected columns; use only the documented metadata columns.')
    if frame.empty or len(frame) > 10000:
        raise ValueError('CSV must contain between 1 and 10,000 rows.')
    try:
        features = frame[required].apply(pd.to_numeric, errors='raise')
    except (ValueError, TypeError) as exc:
        raise ValueError('All feature values must be numeric.') from exc
    if not np.isfinite(features.to_numpy()).all():
        raise ValueError('Missing, NaN and infinite values are not allowed.')
    if not features['packet_size'].between(1, 65535).all():
        raise ValueError('packet_size must be between 1 and 65,535 bytes.')
    if not (features['inter_arrival_time'] >= 0).all():
        raise ValueError('inter_arrival_time must be nonnegative seconds.')
    if not features['direction'].isin([-1, 1]).all():
        raise ValueError('direction must be -1 or 1.')
    if training and set(features['label']) != {0, 1}:
        raise ValueError('Training labels must contain both 0 (benign) and 1 (malicious).')
    return features


def train_model(data_path=DATA_PATH, output_path=MODEL_PATH):
    frame = read_features(data_path, training=True)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(frame[FEATURES], frame['label'].astype(int))
    joblib.dump(model, output_path)
    return model


def load_or_train():
    if MODEL_PATH.exists():
        try:
            model = joblib.load(MODEL_PATH)
            if list(model.feature_names_in_) == FEATURES and set(model.classes_) == {0, 1}:
                return model
        except (ValueError, AttributeError, EOFError, ImportError, pickle.UnpicklingError, OSError, IndexError, KeyError):
            pass
    # Train in memory so first startup works in a read-only deployment.
    frame = read_features(DATA_PATH, training=True)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    return model.fit(frame[FEATURES], frame['label'].astype(int))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DATA_PATH)
    parser.add_argument('--output', type=Path, default=MODEL_PATH)
    args = parser.parse_args()
    try:
        train_model(args.data, args.output)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Training failed: {exc}\n')
    print(f'Model saved to {args.output}. Demo data does not establish real-world accuracy.')
