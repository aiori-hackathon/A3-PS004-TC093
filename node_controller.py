import socket
import hmac
import hashlib
import sys
import time

# Defaults to loopback (127.0.0.1) for single-machine testing
GATEWAY_IP = "127.0.0.1"
GATEWAY_PORT = 8530

VALID_SECRET = b"AIORI_DNSSEC_SECRET_KEY_2026"
ROGUE_SECRET = b"HACKER_FORGED_SECRET_KEY_9999"

def run_query(mode, domain, secret_key, target_ip, tamper_ip=False):
    print("\n" + "="*70)
    if mode == "OWNER":
        print(" [\033[1;32mOWNER MODE\033[0m] Sending Authorized Request from Trusted Client...")
    else:
        print(" [\033[1;31mATTACKER MODE\033[0m] Attempting Over-the-Air Exploitation / Payload Injection...")
    print("="*70)
    print(f" ├── Target Gateway : {target_ip}:{GATEWAY_PORT}")
    print(f" ├── Target Domain  : '{domain}'")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        s.connect((target_ip, GATEWAY_PORT))
        s.sendall(domain.encode())
        data = s.recv(1024)
        s.close()

        if len(data) < 37:
            print(" └── [ERROR] Received incomplete binary frame from gateway.")
            return

        payload_header = bytearray(data[:5])
        received_hmac = data[5:37]

        # Simulate active MITM payload byte alteration over the socket connection
        if tamper_ip:
            print(" ├── \033[1;31m[MITM ATTACK]\033[0m Altering IPv4 payload bytes to 10.0.0.66 (Malicious C2)...")
            payload_header[0] = 10
            payload_header[3] = 66

        # Re-compute HMAC-SHA256 signature locally
        expected_hmac = hmac.new(secret_key, bytes(payload_header), hashlib.sha256).digest()
        ip = '.'.join(str(b) for b in payload_header[:4])
        status = payload_header[4]
        is_valid = (received_hmac == expected_hmac)

        print(f" ├── Received IPv4   : {ip}")
        print(f" ├── DNSSEC Flag     : 0x{status:02X} ({'SECURE' if status == 0 else 'BOGUS'})")
        print(f" ├── HMAC Integrity  : {'MATCH [✓]' if is_valid else 'MISMATCH [✗]'}")

        if is_valid and status == 0:
            print(" └── Security Result : \033[1;32m[ACCESS GRANTED] Payload Authenticated\033[0m")
        elif not is_valid:
            print(" └── Security Result : \033[1;31m[PACKET DISCARDED] HMAC Verification Failed — Attack Mitigated\033[0m")
        else:
            print(" └── Security Result : \033[1;31m[PACKET DROPPED] Gateway Flagged Upstream BOGUS Zone\033[0m")

    except Exception as e:
        print(f" └── [ERROR] Connection failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 node_controller.py owner [OPTIONAL_GATEWAY_IP]")
        print("  python3 node_controller.py hacker [OPTIONAL_GATEWAY_IP]")
        sys.exit(1)

    role = sys.argv[1].lower()
    target_ip = sys.argv[2] if len(sys.argv) > 2 else GATEWAY_IP

    if role == "owner":
        run_query("OWNER", "secure.aiori.lab", VALID_SECRET, target_ip)
    elif role == "hacker":
        print("\n[*] Executing Attack 1: Querying with Unauthenticated Secret Key...")
        run_query("HACKER", "secure.aiori.lab", ROGUE_SECRET, target_ip)
        time.sleep(1.2)
        print("\n[*] Executing Attack 2: Intercepting and Altering IPv4 Bytes (MITM)...")
        run_query("HACKER", "secure.aiori.lab", VALID_SECRET, target_ip, tamper_ip=True)
    else:
        print("Invalid role. Use 'owner' or 'hacker'.")
