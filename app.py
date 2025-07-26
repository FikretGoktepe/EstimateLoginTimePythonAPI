import os
import json
import time
import requests
import pandas as pd
from flask import Flask, jsonify
from prophet import Prophet
from sklearn.neural_network import MLPRegressor

app = Flask(__name__)

cacheFile = "cache.json"

#API Fetch isteði
def fetch_data():
    resp = requests.get("https://case-test-api.humanas.io")
    resp.raise_for_status()
    return resp.json()

#Prophet ve Neural Prophet için dataframe ayarlanýyor.
def prepare_df(timestamps):
    df = pd.DataFrame({'ds': pd.to_datetime(timestamps)})
    df['ds'] = df['ds'].dt.tz_localize(None)
    df = df.groupby('ds').size().reset_index(name='y')
    df = df.set_index('ds').asfreq('D', fill_value=0).reset_index()
    return df

# Prophet ile tahmin yapýlýyor
def prophet_predict(timestamps):
    if len(timestamps) < 3:
        return None
    df = prepare_df(timestamps)
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=1)
    forecast = model.predict(future)
    next_point = forecast.tail(1).iloc[0]
    return next_point['ds'].isoformat()

# Neural Prophet ile tahmin yapýlýyor
def neural_predict(timestamps):
    if len(timestamps) < 6:
        return "ERROR_17"
    df = prepare_df(timestamps)
    y = df['y'].values
    X = []
    Y = []
    # Veriler 3 er 3 er gruplanarak model için örnekler oluþturuluyor
    window_size = 3
    for i in range(len(y) - window_size):
        X.append(y[i:i+window_size])
        Y.append(y[i+window_size])
    if not X:
        return None
    model = MLPRegressor(hidden_layer_sizes=(50,), max_iter=500)
    model.fit(X, Y)
    last_window = y[-window_size:]
    pred = model.predict([last_window])[0]
    pred_date = df['ds'].max() + pd.Timedelta(days=1)
    return pred_date.isoformat()

#Cache yenilenmesi API üzerinden veriler alýnarak hesaplanýyor ve cache temp olarak ayrý bir dosyaya yazýlýyor iþlem bitiðinde cache.json dosyasý deðiþtiriliyor.
def update_cache():
    try:
        data = fetch_data()
        cache = {}
        for user in data['data']['rows']:
            uid = user['id']
            logins = user.get('logins', [])
            p_predicted = prophet_predict(logins)
            np_predicted = neural_predict(logins)
            cache[uid] = {
                "resultP": p_predicted,
                "resultNP": np_predicted
            }
        # Cache yazýmý sýrasýnda bir istek gelirse hata oluþmamasý adýna öncelikle farklý bir dosyaya yazým yapýlýp iþlem bitince cache dosyasýyla deðiþtiriliyor.
        with open(cacheFile + ".tmp", "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        os.replace(cacheFile + ".tmp", cacheFile)
    except Exception as e:
        print(f"Cache update error: {e}")

#API Isteði için Route
@app.route('/estimated-time')
def get_predictions():
    try:
        with open(cacheFile, "r", encoding="utf-8") as f:
            cache = json.load(f)
        return jsonify({"status": 1, "data": cache})
    except Exception as e:
        return jsonify({"status": 0, "data": "ERROR_16"})

    # Her 15 dk geçtiðinde cache kendini yeniliyor.
def periodic_cache_update():
    while True:
        update_cache()
        time.sleep(15*60)

if __name__ == '__main__':
    import threading
    # Cache güncellenirken istek alýnabilmesi için iþlem arkaplanda yapýlýyor.
    t = threading.Thread(target=periodic_cache_update, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
