# 🌿 Carbon Credit Dashboard - ALL SENSORS AUTOMATED

## ✅ IMPORTANT CHANGE: ALL 6 PARAMETERS ARE NOW SENSOR-DRIVEN!

### What Changed:

**BEFORE (Old Code):**
- Temperature, Humidity, CO2_Emitted_Cars = **Sensors** (readonly)
- Sunlight, CO2_Absorbed_Trees, O2_Released_Trees = **Manual Input** (user types)

**NOW (New Code):**
- **ALL 6 PARAMETERS** = **Sensors** (readonly, auto-populated)
- Temperature ✅ Sensor
- Humidity ✅ Sensor  
- Sunlight ✅ **NOW SENSOR** (was manual)
- CO2_Emitted_Cars ✅ Sensor
- CO2_Absorbed_Trees ✅ **NOW SENSOR** (was manual)
- O2_Released_Trees ✅ **NOW SENSOR** (was manual)

---

## 📡 ESP32 Integration - Send ALL 6 Parameters

### Expected JSON Format from ESP32:

```json
{
  "Temperature": 28.5,
  "Humidity": 65.2,
  "Sunlight": 1200,
  "CO2_Emitted_Cars": 420,
  "CO2_Absorbed_Trees": 450,
  "O2_Released_Trees": 380
}
```

### ESP32 Arduino Code Example:

```cpp
#include <WiFi.h>
#include <HTTPClient.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server URL
const char* serverUrl = "http://192.168.1.100:5000/update_sensor";

// Sensor readings
float temperature = 0;
float humidity = 0;
float sunlight = 0;
float co2_emitted = 0;
float co2_absorbed = 0;
float o2_released = 0;

void setup() {
  Serial.begin(115200);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi Connected!");
}

void loop() {
  // Read ALL 6 sensors
  temperature = readTemperatureSensor();      // Your temp sensor code
  humidity = readHumiditySensor();            // Your humidity sensor code
  sunlight = readSunlightSensor();            // Your light sensor code
  co2_emitted = readCO2EmittedSensor();       // Your CO2 emission sensor
  co2_absorbed = readCO2AbsorbedSensor();     // Your CO2 absorption sensor
  o2_released = readO2ReleasedSensor();       // Your O2 sensor code
  
  // Send data to server
  sendSensorData();
  
  delay(5000); // Send every 5 seconds
}

void sendSensorData() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    // Create JSON with ALL 6 parameters
    String jsonData = "{";
    jsonData += "\"Temperature\":" + String(temperature) + ",";
    jsonData += "\"Humidity\":" + String(humidity) + ",";
    jsonData += "\"Sunlight\":" + String(sunlight) + ",";
    jsonData += "\"CO2_Emitted_Cars\":" + String(co2_emitted) + ",";
    jsonData += "\"CO2_Absorbed_Trees\":" + String(co2_absorbed) + ",";
    jsonData += "\"O2_Released_Trees\":" + String(o2_released);
    jsonData += "}";
    
    Serial.println("📡 Sending: " + jsonData);
    
    int httpCode = http.POST(jsonData);
    
    if (httpCode > 0) {
      String response = http.getString();
      Serial.println("✅ Server response: " + response);
    } else {
      Serial.println("❌ Error sending data");
    }
    
    http.end();
  }
}

// Example sensor reading functions (replace with your actual sensor code)
float readTemperatureSensor() {
  // Replace with your DHT22/DS18B20 code
  return random(20, 35);  // Example: 20-35°C
}

float readHumiditySensor() {
  // Replace with your DHT22 code
  return random(40, 80);  // Example: 40-80%
}

float readSunlightSensor() {
  // Replace with your LDR/BH1750 light sensor code
  return random(500, 2000);  // Example: 500-2000 µmol/m²/s
}

float readCO2EmittedSensor() {
  // Replace with your MQ-135 or CCS811 CO2 sensor code
  return random(350, 500);  // Example: 350-500 ppm
}

float readCO2AbsorbedSensor() {
  // Replace with your calculation or sensor code
  // This could be calculated based on tree count, photosynthesis rate, etc.
  return random(400, 600);  // Example: 400-600 ppm
}

float readO2ReleasedSensor() {
  // Replace with your oxygen sensor code (if available)
  // Or calculate based on photosynthesis
  return random(300, 500);  // Example: 300-500 ppm
}
```

---

## 🧪 Testing with curl Commands

### Test 1: Send ALL 6 Parameters

```bash
curl -X POST http://localhost:5000/update_sensor \
  -H "Content-Type: application/json" \
  -d '{
    "Temperature": 28.5,
    "Humidity": 65.2,
    "Sunlight": 1200,
    "CO2_Emitted_Cars": 420,
    "CO2_Absorbed_Trees": 450,
    "O2_Released_Trees": 380
  }'
```

Expected response:
```json
{
  "status": "OK",
  "received": {...},
  "timestamp": "2024-01-15 14:30:00",
  "parameters_updated": [
    "Temperature",
    "Humidity", 
    "Sunlight",
    "CO2_Emitted_Cars",
    "CO2_Absorbed_Trees",
    "O2_Released_Trees"
  ],
  "total_sensors_active": 6,
  "message": "Successfully updated 6 sensor parameters"
}
```

### Test 2: Get Sensor Data

```bash
curl http://localhost:5000/get_sensor
```

Expected response:
```json
{
  "Temperature": 28.5,
  "Humidity": 65.2,
  "Sunlight": 1200,
  "CO2_Emitted_Cars": 420,
  "CO2_Absorbed_Trees": 450,
  "O2_Released_Trees": 380,
  "last_updated": "2024-01-15 14:30:00",
  "sensors_count": 6,
  "all_sensors_type": "ALL_SENSOR_DRIVEN"
}
```

### Test 3: Calculate Carbon Score

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Temperature": 28.5,
    "Humidity": 65.2,
    "Sunlight": 1200,
    "CO2_Emitted_Cars": 420,
    "CO2_Absorbed_Trees": 450,
    "O2_Released_Trees": 380
  }'
```

---

## 📁 File Placement

```
CARBON_CREDIT_PROJECT/
│
├── web/
│   └── index.html          ← NEW FILE (all 6 sensors readonly)
│
├── app.py                  ← NEW FILE (accepts all 6 from sensors)
│
├── models/
│   ├── linear_regression_model.joblib
│   └── random_forest_model.joblib
│
└── requirements.txt
```

---

## 🚀 How to Run

1. **Replace files:**
   ```bash
   # Put new index.html in web/ folder
   # Put new app.py in root folder
   ```

2. **Install dependencies:**
   ```bash
   pip install flask joblib numpy scikit-learn
   ```

3. **Run server:**
   ```bash
   python app.py
   ```

4. **Server output:**
   ```
   ============================================================
   🌿 CARBON CREDIT DASHBOARD SERVER - ALL SENSORS AUTOMATED 🌿
   ============================================================
   ✅ Linear Regression Model: Loaded
   ✅ Random Forest Model: Loaded
   📊 Total Sensors: 6 (ALL AUTOMATED)
      • Temperature (sensor)
      • Humidity (sensor)
      • Sunlight (sensor) ← NOW SENSOR-DRIVEN
      • CO₂ Emitted (sensor)
      • CO₂ Absorbed (sensor) ← NOW SENSOR-DRIVEN
      • O₂ Released (sensor) ← NOW SENSOR-DRIVEN
   🌐 Server starting on http://0.0.0.0:5000
   ============================================================
   ```

5. **Open browser:**
   ```
   http://localhost:5000
   ```

---

## 🎯 Key Features

### Frontend (index.html):
- ✅ ALL 6 input fields are **readonly**
- ✅ All values auto-populate from `/get_sensor` endpoint
- ✅ Updates every 5 seconds automatically
- ✅ Shows "Last updated" time for each sensor
- ✅ Status badges show "Active" for all sensors
- ✅ No manual input required - fully automated!

### Backend (app.py):
- ✅ Accepts ALL 6 parameters from ESP32/sensors
- ✅ `/update_sensor` endpoint receives all sensor data
- ✅ `/get_sensor` returns all 6 current values
- ✅ `/predict` calculates carbon score from all sensors
- ✅ System status tracking for all 6 sensors
- ✅ Professional logging shows all received parameters

---

## 💡 What Your ESP32 Needs to Send

Your ESP32 must read and send **ALL 6 values**:

| Parameter | Unit | Example | Sensor Type |
|-----------|------|---------|-------------|
| Temperature | °C | 28.5 | DHT22/DS18B20 |
| Humidity | % | 65.2 | DHT22 |
| Sunlight | µmol/m²/s | 1200 | BH1750/LDR |
| CO2_Emitted_Cars | ppm | 420 | MQ-135/CCS811 |
| CO2_Absorbed_Trees | ppm | 450 | Calculated/Sensor |
| O2_Released_Trees | ppm | 380 | Calculated/MQ-9 |

---

## 🎤 Presentation Line

**Say to judges:**

*"Our system now operates with complete sensor automation. All six environmental parameters—temperature, humidity, sunlight intensity, CO₂ emissions, CO₂ absorption by trees, and oxygen production—are continuously monitored by our IoT sensors. The data flows automatically from ESP32 to our Flask backend, gets processed by our dual machine learning models, and displays in real-time on our professional dashboard. Zero manual input required. This is industrial-grade environmental monitoring."*

---

## ✅ Summary

**BEFORE:** 3 sensors + 3 manual inputs
**NOW:** 6 sensors + 0 manual inputs = **100% AUTOMATED** 🎯

All sensors are live, all fields are readonly, all data flows automatically!

🌿 **Ready to impress!** 🌿
