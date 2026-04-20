/*
 * Knicks ESP32 Live Scoreboard
 *
 * Hardware:
 *   - ESP32 dev board (any variant)
 *   - SSD1306 0.96" OLED display (128x64, I2C)
 *
 * Wiring (OLED -> ESP32):
 *   VCC  ->  3.3V
 *   GND  ->  GND
 *   SDA  ->  GPIO 21
 *   SCL  ->  GPIO 22
 *
 * Libraries — install via Arduino Library Manager:
 *   - ArduinoJson        (Benoit Blanchon, v6.x)
 *   - Adafruit SSD1306
 *   - Adafruit GFX Library
 *
 * Board: "ESP32 Dev Module" (or your specific variant)
 * Data: ESPN public scoreboard API — no API key required
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ---- CONFIGURE THESE ----
const char* SSID     = "YOUR_WIFI_SSID";
const char* PASSWORD = "YOUR_WIFI_PASSWORD";
// -------------------------

#define SDA_PIN    21
#define SCL_PIN    22
#define SCREEN_W  128
#define SCREEN_H   64
#define OLED_ADDR 0x3C

Adafruit_SSD1306 oled(SCREEN_W, SCREEN_H, &Wire, -1);

const char* ESPN_URL =
  "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard";

const unsigned long POLL_LIVE_MS = 1000UL;                // 1 s during game
const unsigned long POLL_IDLE_MS =  5UL * 60UL * 1000UL; // 5 min otherwise

// ---------------------------------------------------------------------------
// Data model
// ---------------------------------------------------------------------------

struct Game {
  bool   live     = false;
  bool   found    = false;
  int    nykScore = 0;
  int    oppScore = 0;
  String oppAbbr;
  String detail;   // e.g. "Q3 4:21", "Halftime", "Final", "7:30 PM ET"
};

// ---------------------------------------------------------------------------
// Display
// ---------------------------------------------------------------------------

void oledSimple(const char* line1, const char* line2 = nullptr) {
  oled.clearDisplay();
  oled.setTextColor(SSD1306_WHITE);
  if (line2) {
    oled.setTextSize(1);
    oled.setCursor(0, 18);
    oled.println(line1);
    oled.setCursor(0, 36);
    oled.println(line2);
  } else {
    oled.setTextSize(1);
    oled.setCursor(0, 28);
    oled.println(line1);
  }
  oled.display();
}

void oledScore(const Game& g) {
  oled.clearDisplay();
  oled.setTextColor(SSD1306_WHITE);

  char buf[8];

  // --- NYK row ---
  oled.setTextSize(2);          // 12x16 px per char
  oled.setCursor(0, 4);
  oled.print("NYK");
  sprintf(buf, "%3d", g.nykScore);
  oled.setCursor(92, 4);        // right-align: 128 - 3*12 = 92
  oled.print(buf);

  // --- separator ---
  oled.drawFastHLine(0, 26, 128, SSD1306_WHITE);

  // --- Opponent row ---
  oled.setCursor(0, 30);
  oled.print(g.oppAbbr.substring(0, 3));
  sprintf(buf, "%3d", g.oppScore);
  oled.setCursor(92, 30);
  oled.print(buf);

  // --- lead pill (centre gap) ---
  int lead = g.nykScore - g.oppScore;
  if (lead != 0) {
    oled.setTextSize(1);
    char leadBuf[8];
    snprintf(leadBuf, sizeof(leadBuf), lead > 0 ? "+%d" : "%d", lead);
    // centre the string (6px per char at size 1)
    int x = (128 - (int)strlen(leadBuf) * 6) / 2;
    oled.setCursor(x, 10);
    oled.print(leadBuf);
  }

  // --- status line ---
  oled.drawFastHLine(0, 52, 128, SSD1306_WHITE);
  oled.setTextSize(1);
  oled.setCursor(2, 56);
  oled.print(g.detail.substring(0, 21));

  oled.display();
}

// ---------------------------------------------------------------------------
// WiFi
// ---------------------------------------------------------------------------

void connectWiFi() {
  oledSimple("Connecting...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASSWORD);
  for (int i = 0; i < 40 && WiFi.status() != WL_CONNECTED; i++) {
    delay(500);
  }
  if (WiFi.status() != WL_CONNECTED) {
    oledSimple("WiFi failed!", "Check creds.");
  }
}

// ---------------------------------------------------------------------------
// ESPN API
// ---------------------------------------------------------------------------

Game fetchGame() {
  Game g;

  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (WiFi.status() != WL_CONNECTED) return g;

  HTTPClient http;
  http.begin(ESPN_URL);
  http.setTimeout(10000);
  int code = http.GET();
  if (code != HTTP_CODE_OK) {
    http.end();
    return g;
  }

  // Minimal filter so we only allocate the fields we need
  StaticJsonDocument<512> flt;
  JsonObject fevt = flt["events"].createNestedObject();
  fevt["status"]["type"]["name"]        = true;
  fevt["status"]["type"]["shortDetail"] = true;
  JsonObject fcomp = fevt["competitions"].createNestedObject();
  JsonObject fteam = fcomp["competitors"].createNestedObject();
  fteam["team"]["abbreviation"] = true;
  fteam["score"]                = true;

  DynamicJsonDocument doc(12288);
  DeserializationError err =
    deserializeJson(doc, http.getStream(), DeserializationOption::Filter(flt));
  http.end();
  if (err) return g;

  for (JsonObject evt : doc["events"].as<JsonArray>()) {
    JsonArray comps = evt["competitions"].as<JsonArray>();
    if (comps.isNull()) continue;

    for (JsonObject comp : comps) {
      JsonArray teams = comp["competitors"].as<JsonArray>();
      if (teams.isNull()) continue;

      bool   hasNYK  = false;
      int    nykSc   = 0;
      int    oppSc   = 0;
      String oppAb;

      for (JsonObject t : teams) {
        const char* abbr  = t["team"]["abbreviation"];
        const char* score = t["score"];
        int sc = (score && *score) ? atoi(score) : 0;

        if (abbr && strcmp(abbr, "NYK") == 0) {
          hasNYK = true;
          nykSc  = sc;
        } else if (abbr) {
          oppSc = sc;
          oppAb = abbr;
        }
      }

      if (hasNYK) {
        g.found    = true;
        g.nykScore = nykSc;
        g.oppScore = oppSc;
        g.oppAbbr  = oppAb;
        g.detail   = evt["status"]["type"]["shortDetail"].as<String>();

        String sn = evt["status"]["type"]["name"].as<String>();
        g.live = (sn == "STATUS_IN_PROGRESS" || sn == "STATUS_HALFTIME");
        return g;
      }
    }
  }
  return g;
}

// ---------------------------------------------------------------------------
// Arduino entry points
// ---------------------------------------------------------------------------

void setup() {
  Wire.begin(SDA_PIN, SCL_PIN);
  if (!oled.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    for (;;) delay(1000); // OLED not found — halt
  }
  oled.clearDisplay();
  oled.display();

  connectWiFi();
}

void loop() {
  Game g = fetchGame();

  if (g.live) {
    oledScore(g);
    delay(POLL_LIVE_MS);
  } else if (g.found) {
    // Game scheduled or final — show matchup + status
    char line1[32];
    snprintf(line1, sizeof(line1), "NYK vs %s", g.oppAbbr.substring(0, 3).c_str());
    oledSimple(line1, g.detail.c_str());
    delay(POLL_IDLE_MS);
  } else {
    oledSimple("NO GAME TODAY", "  GO KNICKS!");
    delay(POLL_IDLE_MS);
  }
}
