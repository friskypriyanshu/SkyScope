from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_KEY = "9d6eb6d3a3763e5ea98a5c431abac4ff"
OWM_BASE = "https://api.openweathermap.org/data/2.5"


@app.route('/analyze-weather', methods=['POST'])
def analyze():
    data  = request.json
    temp  = data.get('temp', 25)
    wind  = data.get('wind', 10)
    desc  = data.get('description', '').lower()
    uv    = data.get('uv_index', 3)

   
    score = 10
    if temp > 38 or temp < 0:   score -= 5
    elif temp > 32 or temp < 8: score -= 2
    if wind > 30:  score -= 2
    elif wind > 20: score -= 1
    if any(w in desc for w in ['rain','storm','thunder','snow','shower']): score -= 4
    elif any(w in desc for w in ['haze','mist','fog','smog']): score -= 2
    if uv >= 8:  score -= 2
    elif uv >= 6: score -= 1
    score = max(0, min(10, score))

    if score >= 8:   activity_msg = "🏃 Great day for outdoor activities!"
    elif score >= 5: activity_msg = "🚶 Moderate conditions — plan accordingly."
    elif score >= 3: activity_msg = "😐 Not ideal, but manageable indoors."
    else:            activity_msg = "🏠 Stay indoors. Conditions are rough."

    
    rain_kw = ['rain','drizzle','storm','snow','shower','sleet']
    if any(w in desc for w in rain_kw):
        car_wash       = "❌ Don't wash your car. Rain predicted!"
        cw_color       = "#ff5252"
    elif any(w in desc for w in ['haze','dust','smog','sand']):
        car_wash       = "⚠️ Dusty — wash but expect quick re-dust."
        cw_color       = "#ffd600"
    else:
        car_wash       = "✅ Perfect day for a car wash!"
        cw_color       = "#69f0ae"

 
    if uv <= 0:
        sun_msg  = "☁️ No UV risk right now."
        uv_class = "low"
    elif uv <= 2:
        sun_msg  = f"🌥️ Low UV ({uv}). No SPF needed."
        uv_class = "low"
    elif uv <= 5:
        burn     = round(200 / uv)
        sun_msg  = f"🕶️ Moderate UV ({uv}). Burn in ~{burn} min. Use SPF 30."
        uv_class = "moderate"
    elif uv <= 7:
        burn     = round(200 / uv)
        sun_msg  = f"⚠️ High UV ({uv}). Burn in ~{burn} min. SPF 50+ advised."
        uv_class = "high"
    else:
        burn     = round(200 / uv)
        sun_msg  = f"🚨 Very High UV ({uv})! Burn in ~{burn} min. Stay shaded."
        uv_class = "danger"

    
    if temp <= 5:    clothing = "🧥 Heavy jacket + gloves + scarf"
    elif temp <= 15: clothing = "🧣 Jacket + warm layers"
    elif temp <= 22: clothing = "👔 Light jacket or hoodie"
    elif temp <= 30: clothing = "👕 T-shirt weather, stay hydrated"
    elif temp <= 36: clothing = "🩳 Light breathable clothing + hat"
    else:            clothing = "🌂 Minimal clothing + sun protection"

    return jsonify({
        "score":          score,
        "activity_msg":   activity_msg,
        "car_wash":       car_wash,
        "car_wash_color": cw_color,
        "sun_advice":     sun_msg,
        "uv_class":       uv_class,
        "clothing":       clothing,
        "uv_val":         uv,
        "bg_type":        "warm" if temp > 22 else "cold"
    })


@app.route('/weather', methods=['GET'])
def live_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "lat and lon required"}), 400
    try:
        r = requests.get(f"{OWM_BASE}/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric")
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/forecast', methods=['GET'])
def live_forecast():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "lat and lon required"}), 400
    try:
        r = requests.get(f"{OWM_BASE}/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric")
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/uvi', methods=['GET'])
def live_uvi():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "lat and lon required"}), 400
    try:
        r = requests.get(f"{OWM_BASE}/uvi?lat={lat}&lon={lon}&appid={API_KEY}")
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "SkyScope backend running ✅", "version": "1.0"})

if __name__ == '__main__':
    print("🌤️  SkyScope Flask backend starting on http://localhost:5000")
    app.run(port=5000, debug=True)
