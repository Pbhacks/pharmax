#include <ESP8266WiFi.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>
#include <NewPing.h>

// WiFi Credentials
const char* WIFI_SSID = "YourWiFiSSID";
const char* WIFI_PASSWORD = "YourWiFiPassword";

// Explicit NodeMCU Pin Mapping
#define DHTPIN 4            // GPIO4 (D2)
#define TRIGGER_PIN 12       // GPIO12 (D6)
#define ECHO_PIN 13          // GPIO13 (D7)
#define BUTTON_PIN 5         // GPIO5 (D1)
#define GREEN_LED 0          // GPIO0 (D3)
#define RED_LED 2            // GPIO2 (D4)

#define DHTTYPE DHT11        // DHT 11 Sensor Type
#define SCREEN_WIDTH 128     // OLED display width
#define SCREEN_HEIGHT 64     // OLED display height
#define OLED_RESET -1        // Reset pin # 

// Object Initializations
DHT dht(DHTPIN, DHTTYPE);
NewPing sonar(TRIGGER_PIN, ECHO_PIN);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Global Variables
float temperature = 0.0;
float humidity = 0.0;
int distance = 0;
bool alertMode = false;

// Thresholds
const int TEMP_THRESHOLD_HIGH = 35;  // High temperature warning
const int TEMP_THRESHOLD_LOW = 10;   // Low temperature warning
const int DISTANCE_THRESHOLD = 20;   // Proximity alert in cm

void setup() {
  Serial.begin(115200);
  
  // WiFi Connection
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected");

  // OLED Display Initialization
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); 
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  // Pin Mode Setup
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  
  // Sensor Initializations
  dht.begin();

  // Initial Display
  displayWelcomeScreen();
}

void loop() {
  readSensors();
  checkEnvironmentalConditions();
  updateDisplay();
  
  if(digitalRead(BUTTON_PIN) == LOW) {
    resetAlert();
    delay(500); 
  }
  
  delay(2000); 
}

void readSensors() {
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  distance = sonar.ping_cm();
}

void checkEnvironmentalConditions() {
  if(temperature > TEMP_THRESHOLD_HIGH || temperature < TEMP_THRESHOLD_LOW) {
    triggerAlert("TEMP ALERT!");
  }
  
  if(distance > 0 && distance < DISTANCE_THRESHOLD) {
    triggerAlert("PROXIMITY WARN!");
  }
}

void triggerAlert(String alertMessage) {
  alertMode = true;
  digitalWrite(RED_LED, HIGH);
  
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(0,0);
  display.println(alertMessage);
  display.display();
}

void resetAlert() {
  alertMode = false;
  digitalWrite(RED_LED, LOW);
  updateDisplay();
}

void updateDisplay() {
  if(!alertMode) {
    display.clearDisplay();
    display.setTextSize(1);
    
    display.setCursor(0,0);
    display.print("Temp: ");
    display.print(temperature);
    display.println(" C");
    
    display.print("Humidity: ");
    display.print(humidity);
    display.println(" %");
    
    display.print("Distance: ");
    display.print(distance);
    display.println(" cm");
    
    display.display();
  }
}

void displayWelcomeScreen() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(10,0);
  display.println("Smart Agri");
  display.setTextSize(1);
  display.setCursor(15,40);
  display.println("IoT Monitoring");
  display.display();
  delay(2000);
}