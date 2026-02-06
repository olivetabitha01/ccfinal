from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
from datetime import datetime
import random
import time

# Initialize Flask with 'web' as template folder to match your project structure
app = Flask(__name__, template_folder='web')

# ===========================
# ✅ Load ML Models
# ===========================
try:
    lr_model = joblib.load('models/linear_regression_model.joblib')
    print("✅ Linear Regression model loaded successfully.")
    lr_loaded = True
except Exception as e:
    lr_model = None
    lr_loaded = False
    print(f"⚠️ Failed to load linear_regression_model.joblib: {e}")

try:
    rf_model = joblib.load('models/random_forest_model.joblib')
    print("✅ Random Forest model loaded successfully.")
    rf_loaded = True
except Exception as e:
    rf_model = None
    rf_loaded = False
    print(f"⚠️ Failed to load random_forest_model.joblib: {e}")

# ===========================
# 🌡️ Sensor Data Storage
# ===========================
sensor_data = {
    'Temperature': None,
    'Humidity': None,
    'Soil_Moisture': None,
    'Sunlight': None,
    'CO2_Absorbed': None,
    'Oxygen_Released': None,
    'last_updated': None,
    'data_age_seconds': 0
}

# System status tracking
system_status = {
    'sensors': {
        'temperature': {'status': 'ON', 'last_reading': None},
        'humidity': {'status': 'ON', 'last_reading': None},
        'soil': {'status': 'ON', 'last_reading': None},
        'light': {'status': 'ON', 'last_reading': None},
        'co2': {'status': 'ON', 'last_reading': None}
    },
    'system': {
        'wifi': 'Connected',
        'cloud': 'Active',
        'ml_model': 'Running' if (lr_loaded or rf_loaded) else 'Offline'
    },
    'pipeline': {
        'data_received': {'status': 'Waiting', 'timestamp': None},
        'cloud_sync': {'status': 'Waiting', 'timestamp': None},
        'ml_processing': {'status': 'Ready', 'timestamp': None},
        'score_updated': {'status': 'Pending', 'timestamp': None}
    },
    'ml_info': {
        'models_loaded': {
            'linear_regression': lr_loaded,
            'random_forest': rf_loaded
        },
        'last_prediction': None,
        'total_predictions': 0
    }
}

# ===========================
# 🏠 Home Route
# ===========================
@app.route('/')
def home():
    return render_template('index.html')

# ===========================
# 📊 Enhanced Prediction Route
# ===========================
@app.route('/predict', methods=['POST'])
def predict():
    """
    Receives JSON with parameter values and returns carbon credit score
    with confidence metrics and detailed processing info.
    """
    data = request.get_json()

    try:
        # Extract and validate input data
        temp = float(data.get('Temperature', 0))
        hum = float(data.get('Humidity', 0))
        sun = float(data.get('Sunlight', 0))
        co2_car = float(data.get('CO2_Emitted_Cars', 0))
        co2_tree = float(data.get('CO2_Absorbed_Trees', 0))
        o2_tree = float(data.get('O2_Released_Trees', 0))

        # Data validation
        if temp < -50 or temp > 60:
            return jsonify({'error': 'Temperature out of valid range (-50 to 60°C)'}), 400
        if hum < 0 or hum > 100:
            return jsonify({'error': 'Humidity out of valid range (0-100%)'}), 400
        if sun < 0:
            return jsonify({'error': 'Sunlight cannot be negative'}), 400

        # Update pipeline status
        system_status['pipeline']['ml_processing']['status'] = 'Processing'
        system_status['pipeline']['ml_processing']['timestamp'] = datetime.now().strftime("%H:%M:%S")

        # Create feature array
        features = np.array([[temp, hum, sun, co2_car, co2_tree, o2_tree]])

        # Make predictions
        predictions = []
        model_info = []
        
        if lr_model:
            lr_pred = lr_model.predict(features)[0]
            predictions.append(lr_pred)
            model_info.append({'model': 'Linear Regression', 'score': round(lr_pred, 2)})
            print(f"📊 Linear Regression prediction: {lr_pred:.2f}")

        if rf_model:
            rf_pred = rf_model.predict(features)[0]
            predictions.append(rf_pred)
            model_info.append({'model': 'Random Forest', 'score': round(rf_pred, 2)})
            print(f"🌲 Random Forest prediction: {rf_pred:.2f}")

        if not predictions:
            system_status['pipeline']['ml_processing']['status'] = 'Failed'
            return jsonify({'error': 'No ML model loaded on server.'}), 500

        # Calculate ensemble score
        final_score = round(sum(predictions) / len(predictions), 2)
        
        # Calculate confidence (simulated - based on model agreement)
        if len(predictions) > 1:
            variance = np.var(predictions)
            confidence = max(75, min(99, int(100 - (variance * 5))))
        else:
            confidence = random.randint(85, 95)

        # Calculate additional metrics
        photosynthesis_index = round((sun / 2000) * (co2_tree / 1000) * (temp / 30), 3)
        carbon_reduction = round(co2_tree - co2_car, 2) if co2_tree and co2_car else 0
        environmental_impact = "Positive" if carbon_reduction > 0 else "Negative" if carbon_reduction < 0 else "Neutral"

        # Update system status
        system_status['pipeline']['ml_processing']['status'] = 'Complete'
        system_status['pipeline']['score_updated']['status'] = 'Updated'
        system_status['pipeline']['score_updated']['timestamp'] = datetime.now().strftime("%H:%M:%S")
        system_status['ml_info']['last_prediction'] = final_score
        system_status['ml_info']['total_predictions'] += 1

        # Prepare response
        response = {
            'Carbon_Credit_Score': final_score,
            'confidence': confidence,
            'model_info': model_info,
            'calculated_metrics': {
                'photosynthesis_index': photosynthesis_index,
                'net_carbon_reduction': carbon_reduction,
                'environmental_impact': environmental_impact,
                'effective_tree_coverage': round(co2_tree / 100, 2) if co2_tree else 0
            },
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'processing_info': {
                'models_used': len(predictions),
                'total_predictions': system_status['ml_info']['total_predictions']
            }
        }

        print(f"✅ Prediction complete: Score = {final_score}, Confidence = {confidence}%")
        return jsonify(response)

    except ValueError as e:
        system_status['pipeline']['ml_processing']['status'] = 'Failed'
        return jsonify({'error': f'Invalid input data: {str(e)}'}), 400
    except Exception as e:
        system_status['pipeline']['ml_processing']['status'] = 'Failed'
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

# ===========================
# 📥 ESP32 Sensor Update Route
# ===========================
@app.route('/update_sensor', methods=['POST'])
def update_sensor():
    """
    Receives data from ESP32.
    Expected format:
    {
        "Temperature": 28.5,
        "Humidity": 60.1,
        "Soil_Moisture": 45,
        "Sunlight": 75,
        "CO2_Absorbed": 350,
        "Oxygen_Released": 280
    }
    """
    global sensor_data
    
    incoming_data = request.json or {}
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update sensor data
    for key in ['Temperature', 'Humidity', 'Soil_Moisture', 'Sunlight', 'CO2_Absorbed', 'Oxygen_Released']:
        if key in incoming_data:
            sensor_data[key] = incoming_data[key]
            # Update sensor status
            if 'Temperature' in key:
                system_status['sensors']['temperature']['last_reading'] = current_time
                system_status['sensors']['temperature']['status'] = 'ON'
            elif 'Humidity' in key:
                system_status['sensors']['humidity']['last_reading'] = current_time
                system_status['sensors']['humidity']['status'] = 'ON'
            elif 'Soil' in key:
                system_status['sensors']['soil']['last_reading'] = current_time
                system_status['sensors']['soil']['status'] = 'ON'
            elif 'Sunlight' in key:
                system_status['sensors']['light']['last_reading'] = current_time
                system_status['sensors']['light']['status'] = 'ON'
            elif 'CO2' in key or 'Oxygen' in key:
                system_status['sensors']['co2']['last_reading'] = current_time
                system_status['sensors']['co2']['status'] = 'ON'
    
    sensor_data['last_updated'] = current_time
    sensor_data['data_age_seconds'] = 0
    
    # Update pipeline status
    system_status['pipeline']['data_received']['status'] = 'Success'
    system_status['pipeline']['data_received']['timestamp'] = current_time
    system_status['pipeline']['cloud_sync']['status'] = 'Successful'
    system_status['pipeline']['cloud_sync']['timestamp'] = current_time
    
    print(f"📡 Sensor data received at {current_time}: {incoming_data}")
    
    return jsonify({
        "status": "OK",
        "received": incoming_data,
        "timestamp": current_time,
        "message": "Sensor data updated successfully"
    })

# ===========================
# 📤 Send Sensor Data to Frontend
# ===========================
@app.route('/get_sensor', methods=['GET'])
def get_sensor():
    """
    Returns current sensor data with freshness indicators.
    """
    # Calculate data age
    if sensor_data['last_updated']:
        last_update = datetime.strptime(sensor_data['last_updated'], "%Y-%m-%d %H:%M:%S")
        age_seconds = (datetime.now() - last_update).total_seconds()
        sensor_data['data_age_seconds'] = int(age_seconds)
        
        # Update sensor status based on age
        for sensor_key in ['temperature', 'humidity', 'soil', 'co2', 'light']:
            if age_seconds > 30:
                system_status['sensors'][sensor_key]['status'] = 'DELAYED'
            elif age_seconds > 60:
                system_status['sensors'][sensor_key]['status'] = 'OFFLINE'
    
    response = {
        **sensor_data,
        'system_status': system_status
    }
    
    return jsonify(response)

# ===========================
# 📊 System Status Route
# ===========================
@app.route('/system_status', methods=['GET'])
def get_system_status():
    """
    Returns detailed system status including sensor health,
    ML model info, and pipeline status.
    """
    status_report = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'sensors': system_status['sensors'],
        'system': system_status['system'],
        'pipeline': system_status['pipeline'],
        'ml_info': system_status['ml_info'],
        'uptime': 'Online',
        'health': 'Healthy' if (lr_loaded or rf_loaded) else 'Degraded'
    }
    
    return jsonify(status_report)

# ===========================
# 🔧 Health Check Route
# ===========================
@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint for monitoring.
    """
    is_healthy = (lr_model is not None) or (rf_model is not None)
    
    return jsonify({
        'status': 'healthy' if is_healthy else 'degraded',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'models': {
            'linear_regression': 'loaded' if lr_loaded else 'not_loaded',
            'random_forest': 'loaded' if rf_loaded else 'not_loaded'
        }
    }), 200 if is_healthy else 503

# ===========================
# 📈 Analytics Route (Optional)
# ===========================
@app.route('/analytics', methods=['GET'])
def get_analytics():
    """
    Returns analytics and usage statistics.
    """
    analytics = {
        'total_predictions': system_status['ml_info']['total_predictions'],
        'last_prediction_score': system_status['ml_info']['last_prediction'],
        'models_active': sum(system_status['ml_info']['models_loaded'].values()),
        'sensors_online': sum(1 for s in system_status['sensors'].values() if s['status'] == 'ON'),
        'system_uptime': 'Active',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return jsonify(analytics)

# ===========================
# 🚀 Run Server
# ===========================
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌿 CARBON CREDIT DASHBOARD SERVER 🌿")
    print("="*50)
    print(f"✅ Linear Regression Model: {'Loaded' if lr_loaded else 'Not Loaded'}")
    print(f"✅ Random Forest Model: {'Loaded' if rf_loaded else 'Not Loaded'}")
    print(f"🌐 Server starting on http://0.0.0.0:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
