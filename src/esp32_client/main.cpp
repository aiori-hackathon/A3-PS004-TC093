#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <bearssl/bearssl.h>

WiFiUDP udp;

const char* ssid = "Govt.Pvt_93151";
const char* password = "202401070160";
const uint16_t local_port = 8530;

// Pre-Shared Key (Must match gateway_proxy.py)
const uint8_t SECRET_KEY[] = "aiori_psk_secret_key_2026";

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); // OFF (Active LOW)

  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[+] Wi-Fi Connected!");
  
  udp.begin(local_port);
  Serial.printf("[+] UDP Listener active on port %d\n", local_port);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize == 37) {
    uint8_t buffer[37];
    udp.read(buffer, 37);

    // Parse 37-byte frame: [4B IP] [1B Status] [32B HMAC]
    uint8_t status = buffer[4];
    uint8_t* received_hmac = &buffer[5];

    // Compute local HMAC-SHA256 over the first 5 bytes (IP + Status) using BearSSL
    uint8_t computed_hmac[32];
    br_hmac_context hmac_ctx;
    br_hmac_init(&hmac_ctx, &br_sha256_vtable, SECRET_KEY, sizeof(SECRET_KEY) - 1);
    br_hmac_update(&hmac_ctx, buffer, 5);
    br_hmac_out(&hmac_ctx, computed_hmac);

    // Constant-time cryptographic comparison
    bool hmac_valid = (br_ssl_secure_dercmp(received_hmac, computed_hmac, 32) == 0);

    if (hmac_valid && status == 0x00) {
      // SUCCESS: Valid DNSSEC & Authentic Gateway Frame
      digitalWrite(LED_BUILTIN, LOW); // Flash LED ON
      delay(100);
      digitalWrite(LED_BUILTIN, HIGH); // OFF
      Serial.println("[+] ACCEPT: Valid DNSSEC frame verified securely.");
    } 
    else {
      // FAILURE: Tampered packet, bad HMAC, or BOGUS DNS status!
      for (int i = 0; i < 3; i++) {
        digitalWrite(LED_BUILTIN, LOW);
        delay(50);
        digitalWrite(LED_BUILTIN, HIGH);
        delay(50);
      }
      Serial.println("[-] DROP: Threat neutralized (Bad HMAC, Replay, or Bogus DNS).");
    }
  }
}
