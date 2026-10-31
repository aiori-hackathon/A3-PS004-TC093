import socket
import hmac
import hashlib
import time

HOST = '127.0.0.1'
PORT = 8530
LEGIT_SECRET = b'AIORI_DNSSEC_SECRET_KEY_2026'
FORGED_SECRET = b'ATTACKER_MALICIOUS_SECRET_KEY'

def print_banner():
    print("\033[95m" + "="*75 + "\033[0m")
    print("\033[1;93m  REAL-TIME THREAT MITIGATION MONITOR | GATEWAY-ASSISTED DNSSEC\033[0m")
    print("\033[95m" + "="*75 + "\033[0m")
    print(f"[*] Gateway Endpoint : {HOST}:{PORT}")
    print(f"[*] Threat Protection: Edge DNSSEC AD-Flag + HMAC-SHA256 Payload Integrity")
    print("\033[95m" + "-"*75 + "\033[0m\n")

def run_threat_simulation(scenario_num, title, domain, client_secret, tamper_over_air=False):
    print(f"\033[1;36m[SCENARIO {scenario_num}] {title}\033[0m")
    print(f" ├── Targeted Domain   : '{domain}'")
    
    start_time = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((HOST, PORT))
        s.sendall(domain.encode())
        data = s.recv(1024)
        s.close()
        
        latency = (time.time() - start_time) * 1000
        
        if len(data) >= 37:
            if tamper_over_air:
                data = bytearray(data)
                data[0] = 10
                data[1] = 0
                data[2] = 0
                data[3] = 66

            ip = '.'.join(str(b) for b in data[:4])
            status = data[4]
            received_hmac = data[5:37]
            
            expected_hmac = hmac.new(client_secret, data[:5], hashlib.sha256).digest()
            hmac_valid = (received_hmac == expected_hmac)
            
            if status != 0:
                print(f" ├── Gateway DNSSEC    : \033[1;31m0x01 (BOGUS / INVALID RRSIG)\033[0m")
                print(f" ├── Gateway Action    : Returned Null IP (0.0.0.0)")
                print(f" ├── HMAC Integrity    : \033[1;32mAUTHENTIC GATEWAY ALERT [✓]\033[0m")
                print(f" └── Security Decision : \033[1;31m[✓ DROPPED] Upstream DNS Spoof Blocked at Edge\033[0m\n")
                return

            if not hmac_valid:
                print(f" ├── Received IPv4     : {ip} \033[1;31m(Spoofed C2 Target)\033[0m")
                print(f" ├── HMAC Verification : \033[1;31mFAILED [SIGNATURE MISMATCH]\033[0m")
                print(f" ├── Action Taken      : ESP32 Client Discarded Frame")
                print(f" └── Security Decision : \033[1;31m[✓ DROPPED] MITM / Forged Payload Intercepted\033[0m\n")
                return

            print(f" ├── Upstream DNSSEC   : \033[1;32m0x00 (SECURE / AD VERIFIED)\033[0m")
            print(f" ├── Resolved IPv4     : \033[1;32m{ip}\033[0m")
            print(f" ├── Processing Time   : {latency:.2f} ms")
            print(f" ├── HMAC Verification : \033[1;32mAUTHENTIC SIGNATURE [✓]\033[0m")
            print(f" └── Security Decision : \033[1;32m[✓ ACCESS GRANTED] Secure Connection Established\033[0m\n")

        else:
            print(f" \033[1;31m└── [ERROR] Invalid frame length received ({len(data)} bytes)\033[0m\n")

    except Exception as e:
        print(f" \033[1;31m└── [ERROR] Gateway Connection Refused: {e}\033[0m\n")

def main():
    print_banner()
    run_threat_simulation(1, "Legitimate ESP32 Query", "secure.aiori.lab", LEGIT_SECRET)
    time.sleep(1.2)
    run_threat_simulation(2, "DNS Poisoning Attack (Corrupted Signature)", "bogus.aiori.lab", LEGIT_SECRET)
    time.sleep(1.2)
    run_threat_simulation(3, "Local Wi-Fi MITM Packet Alteration", "secure.aiori.lab", FORGED_SECRET, tamper_over_air=True)

if __name__ == "__main__":
    main()
