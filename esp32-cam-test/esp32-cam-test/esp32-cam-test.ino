#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>

// =================== PINS ===================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// =================== GLOBALS ===================
WebServer server(80);
Preferences preferences;

// Variables to store credentials
String ssid_str = "";
String pass_str = "";
bool wifi_connected = false;

// =================== CAMERA FUNCTIONS ===================
void startCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 15;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

void handleStream() {
  WiFiClient client = server.client();
  String response = "HTTP/1.1 200 OK\r\n";
  response += "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n";
  server.sendContent(response);

  while (client.connected()) {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      continue;
    }
    
    String head = "--frame\r\nContent-Type: image/jpeg\r\n\r\n";
    server.sendContent(head);
    client.write(fb->buf, fb->len);
    server.sendContent("\r\n");
    esp_camera_fb_return(fb);
  }
}

// =================== SETTINGS FUNCTIONS ===================
void handleSetWifi() {
  if (server.hasArg("ssid") && server.hasArg("pass")) {
    String new_ssid = server.arg("ssid");
    String new_pass = server.arg("pass");

    preferences.begin("wifi-creds", false);
    preferences.putString("ssid", new_ssid);
    preferences.putString("pass", new_pass);
    preferences.end();

    server.send(200, "text/plain", "Credentials Saved. Restarting...");
    delay(1000);
    ESP.restart();
  } else {
    server.send(400, "text/plain", "Missing ssid or pass");
  }
}

void setup() {
  Serial.begin(115200);
  startCamera();

  preferences.begin("wifi-creds", true);
  ssid_str = preferences.getString("ssid", "");
  pass_str = preferences.getString("pass", "");
  preferences.end();

  if (ssid_str == "") {
    Serial.println("No SSID saved. Starting AP Mode.");
    WiFi.softAP("ESP32-CAM-SETUP", ""); // No password for setup AP
    Serial.print("Connect to AP: ESP32-CAM-SETUP. IP: ");
    Serial.println(WiFi.softAPIP());
    
    server.on("/set-wifi", handleSetWifi);
    server.begin();
  } else {
    Serial.println("Found Credentials. Connecting to WiFi...");
    WiFi.begin(ssid_str.c_str(), pass_str.c_str());
    
    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
      delay(500);
      Serial.print(".");
      retries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\nWiFi connected");
      Serial.print("Stream URL: http://");
      Serial.print(WiFi.localIP());
      Serial.println("/stream");
      
      // Start Streaming Server
      server.on("/stream", handleStream);
      // Allow re-configuration even if connected
      server.on("/set-wifi", handleSetWifi); 
      server.begin();
      wifi_connected = true;
    } else {
      Serial.println("\nFailed to connect. Resetting preferences and restarting in AP mode.");
      preferences.begin("wifi-creds", false);
      preferences.clear();
      preferences.end();
      ESP.restart();
    }
  }
}

void loop() {
  server.handleClient();
}