
# 🔐 Encrypted Traffic Threat Detection with AI

This project leverages machine learning to detect threats in encrypted network traffic — without decrypting the data. It combines a Flask-based web interface with a Random Forest classifier trained on traffic metadata to provide real-time threat predictions.

---

## 🚀 Project Overview

Traditional security tools struggle to inspect encrypted traffic, leaving blind spots for attackers. This system analyzes metadata such as packet size, timing, and direction to identify malicious patterns using AI — all while preserving encryption.

---

## 🧠 Features

- 📤 Upload encrypted traffic logs via web interface  
- ⚡ Real-time threat classification using AI  
- 🔍 Backend powered by Random Forest model  
- 📊 JSON-based output for easy integration  
- 🧪 Sample dataset and training script included  

---

## 🏗️ Architecture

```
[Web Interface] → [Flask API] → [AI Model]
        ↑                            ↓
[User Uploads CSV] ← [Threat Predictions Returned]
```

---

## 📁 Project Structure

```
Encrypted-Traffic-Threat-Detection/
├── app.py                  # Flask backend
├── train_model.py          # Model training script
├── rf_model.pkl            # Trained Random Forest model
├── traffic_data.csv        # Sample dataset
├── templates/
│   └── index.html          # Upload interface
├── README.md               # Project documentation
```

---

## 📦 Requirements

Install dependencies using pip:

```bash
pip install Flask pandas scikit-learn joblib
```

Or use the included `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 🧪 Dataset Format

The model uses metadata features only:

```csv
packet_size,inter_arrival_time,direction,label
1200,0.02,1,0
800,0.01,-1,1
...
```

- `label`: 0 = benign, 1 = malicious  
- For predictions, omit the `label` column

---

## 🧠 Model Training

Run the training script to generate `rf_model.pkl`:

```bash
python train_model.py
```

This uses `traffic_data.csv` to train a Random Forest classifier.

---

## 🌐 Running the Web App

Start the Flask server:

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.  
Upload a CSV file with traffic metadata to receive threat predictions.

---

## 📊 Sample Output

```json
[
  {"packet_size":1200,"inter_arrival_time":0.02,"direction":1,"Threat":0},
  {"packet_size":800,"inter_arrival_time":0.01,"direction":-1,"Threat":1}
]
```

---

## 📌 Future Enhancements

- Add LSTM or CNN models for deeper pattern recognition  
- Visualize predictions in a dashboard  
- Integrate with live traffic monitoring tools  
- Deploy to cloud platforms (Heroku, AWS, Render)

---

## 📄 License

This project is open-source under the MIT License.  
Feel free to fork, modify, and contribute!

---

## 🙌 Acknowledgments

Developed by [Yogi-TechoMass](https://github.com/Yogi-TechoMass)  
Inspired by the need for smarter encrypted traffic inspection in cybersecurity.
Need help to use this tool,Click here:https://copilot.microsoft.com/shares/VFctKdghYxnDiVUJXVYmb

---
