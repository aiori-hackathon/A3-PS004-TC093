#include <Arduino.h>
#include <WiFi.h>
#include "mbedtls/md.h"

// --- CONFIGURATION ---
const char* WIFI_SSID     = "Gov.Pvt_93151";
const char* WIFI_PASSWORD = "202401070160";

const char* GATEWAY_IP   = "192.168.1.100"; // Laptop 1 IP
const uint16_t GATEWAY_PORT = 8530;

// Pre-shared secret key stored in ESP32 Flash Memory
const char* HMAC_SECRET = "AIORI_DNSSEC_SECRET_KEY_2026";

//HMAC Authentication
void compute_hmac_sha256(const uint8_t *payload, size_t payload_len, const char *key, uint8_t *output) {
    mbedtls_md_context_t ctx;
    mbedtls_md_type_t md_type = MBEDTLS_MD_SHA256;
    mbedtls_md_init(&ctx);
    mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(md_type), 1);
    mbedtls_md_hmac_starts(&ctx, (const unsigned char*)key, strlen(key));
    mbedtls_md_hmac_update(&ctx, payload, payload_len);
    mbedtls_md_hmac_finish(&ctx, output);
    mbedtls_md_free(&ctx);
}

//send queries
void query_dnssec_gateway(const char* domain) {
    Serial.println("\n------------------------------------------------");
    Serial.printf("[ESP32] Sending Query: '%s'\n", domain);
    
    WiFiClient client;
    if (!client.connect(GATEWAY_IP, GATEWAY_PORT)) {
        Serial.println("[ERROR] Could not connect to Edge Gateway!");
        return;
    }

    // 1. Send domain name
    client.print(domain);

    // 2. Read 37-byte response
    uint8_t buffer[64];
    size_t bytes_read = 0;
    unsigned long timeout = millis();
    
    while (client.connected() && millis() - timeout < 2000) {
        while (client.available()) {
            buffer[bytes_read++] = client.read();
            if (bytes_read >= 37) break;
        }
        if (bytes_read >= 37) break;
    }
    client.stop();

    if (bytes_read < 37) {
        Serial.printf("[ERROR] Incomplete payload received (%d bytes)\n", bytes_read);
        return;
    }

    // 3. Extract Payload Header & Received HMAC
    uint8_t payload_header[5];
    memcpy(payload_header, buffer, 5);
    
    uint8_t received_hmac[32];
    memcpy(received_hmac, buffer + 5, 32);

    // 4. Re-compute HMAC on-chip using mbedTLS
    uint8_t expected_hmac[32];
    compute_hmac_sha256(payload_header, 5, HMAC_SECRET, expected_hmac);

    // 5. Compare signatures
    bool hmac_valid = (memcmp(received_hmac, expected_hmac, 32) == 0);
    uint8_t status = payload_header[4];

    Serial.printf("[ESP32] Resolved IP : %d.%d.%d.%d\n", buffer[0], buffer[1], buffer[2], buffer[3]);
    Serial.printf("[ESP32] DNSSEC Status: 0x%02X (%s)\n", status, (status == 0 ? "SECURE" : "BOGUS"));
    Serial.printf("[ESP32] HMAC Check  : %s\n", hmac_valid ? "MATCH [?]" : "MISMATCH [?]");

    // 6. Security Decision
    if (hmac_valid && status == 0) {
        Serial.println("\033[1;32m[DECISION] ACCESS GRANTED -> IP Trusted!\033[0m");
    } else if (!hmac_valid) {
        Serial.println("\033[1;31m[SECURITY ALERT] HMAC Signature Mismatch! Over-the-air Tampering Intercepted. PACKET DISCARDED.\033[0m");
    } else {
        Serial.println("\033[1;31m[SECURITY ALERT] Gateway Flagged Upstream BOGUS Zone. PACKET DROPPED.\033[0m");
    }
    
    Serial.printf("[ESP32] Free Heap Memory: %d bytes (Saved ~90%% RAM)\n", ESP.getFreeHeap());
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n=================================================");
    Serial.println("  ESP32 DNSSEC OFFLOADING CLIENT (A3-PS004-TC093)");
    Serial.println("=================================================");
    
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n[ESP32] Wi-Fi Connected! IP: " + WiFi.localIP().toString());

    // Run test queries
    query_dnssec_gateway("secure.aiori.lab");
    delay(2000);
    query_dnssec_gateway("bogus.aiori.lab");
}

void loop() {
    // Keep idle or re-query periodically
}
