/**
 * ESP32 Client Firmware for Authenticated Gateway-Assisted DNSSEC Offloading
 * Team Code: A3-PS004-TC093 | Problem Statement: PS-004
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include "mbedtls/md.h"

// ==========================================
// CONFIGURATION CONSTANTS
// ==========================================
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

const char* GATEWAY_IP   = "192.168.1.100"; // Replace with your Gateway IP
const uint16_t GATEWAY_PORT = 8530;

const char SHARED_HMAC_KEY[] = "aiori_ps004_secret_key_2026";

// Function Declarations
bool verify_hmac(const uint8_t* payload, size_t len, const uint8_t* received_hmac);
void query_domain(const char* domain_name);

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n==========================================");
    Serial.println(" ESP32 DNSSEC Offloaded Client Initializing");
    Serial.println("==========================================");

    // Initial Heap Check
    Serial.printf("[HEAP] Free Heap before Wi-Fi Connect: %d bytes\n", ESP.getFreeHeap());

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\n[WIFI] Connected! IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.printf("[HEAP] Free Heap after Wi-Fi Connect: %d bytes\n", ESP.getFreeHeap());

    // Run Test Cases
    delay(2000);
    query_domain("secure.aiori.lab");   // Valid DNSSEC
    delay(2000);
    query_domain("bogus.aiori.lab");    // Corrupted DNSSEC (BOGUS)
}

void loop() {
    // Keep idle in demo loop
    delay(10000);
}

void query_domain(const char* domain_name) {
    WiFiClientSecure client;
    client.setInsecure(); // Skip X.509 verification for testing local self-signed cert

    Serial.println("\n------------------------------------------");
    Serial.printf("[QUERY] Initiating resolution for: %s\n", domain_name);
    
    uint32_t start_time = millis();
    uint32_t heap_before = ESP.getFreeHeap();

    if (!client.connect(GATEWAY_IP, GATEWAY_PORT)) {
        Serial.println("[ERROR] Failed to connect to DNSSEC Gateway!");
        return;
    }

    // Send Domain Query
    client.println(domain_name);

    // Read Response Payload (Format: 1 byte status + 4 bytes IP + 32 bytes HMAC)
    uint8_t buffer[37];
    size_t bytes_read = 0;

    while (client.connected() && bytes_read < sizeof(buffer)) {
        if (client.available()) {
            buffer[bytes_read++] = client.read();
        }
    }
    client.stop();

    uint32_t elapsed_time = millis() - start_time;
    uint32_t heap_after = ESP.getFreeHeap();

    if (bytes_read < 37) {
        Serial.printf("[ERROR] Incomplete payload received (%d bytes)\n", bytes_read);
        return;
    }

    uint8_t status_code = buffer[0];
    uint8_t ip_bytes[4] = {buffer[1], buffer[2], buffer[3], buffer[4]};
    uint8_t received_hmac[32];
    memcpy(received_hmac, &buffer[5], 32);

    // Verify HMAC Token using ESP32 Hardware Crypto Engine
    bool is_valid = verify_hmac(buffer, 5, received_hmac);

    if (!is_valid) {
        Serial.println("[SECURITY REJECT] HMAC Authentication Failed! Potential Tampering / Rogue Gateway.");
        return;
    }

    // Parse Results
    if (status_code == 0) {
        Serial.printf("[SUCCESS] Verified IP: %d.%d.%d.%d\n", ip_bytes[0], ip_bytes[1], ip_bytes[2], ip_bytes[3]);
    } else if (status_code == 1) {
        Serial.println("[SECURITY REJECT] Gateway flagged domain as BOGUS (Signature Invalid)!");
    } else {
        Serial.println("[ERROR] Domain Resolution Failed at Gateway.");
    }

    // Metrics Display
    Serial.printf("[METRICS] Execution Time: %d ms\n", elapsed_time);
    Serial.printf("[METRICS] Free Heap Before/After: %d B / %d B (Delta: %d bytes)\n", 
                  heap_before, heap_after, (int32_t)(heap_before - heap_after));
    Serial.println("------------------------------------------");
}

bool verify_hmac(const uint8_t* payload, size_t len, const uint8_t* received_hmac) {
    uint8_t calculated_hmac[32];

    mbedtls_md_context_t ctx;
    mbedtls_md_type_t md_type = MBEDTLS_MD_SHA256;

    mbedtls_md_init(&ctx);
    mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(md_type), 1);
    mbedtls_md_hmac_starts(&ctx, (const unsigned char*)SHARED_HMAC_KEY, strlen(SHARED_HMAC_KEY));
    mbedtls_md_hmac_update(&ctx, payload, len);
    mbedtls_md_hmac_finish(&ctx, calculated_hmac);
    mbedtls_md_free(&ctx);

    return (memcmp(calculated_hmac, received_hmac, 32) == 0);
}
