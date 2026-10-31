import socket
import hmac
import hashlib
import os

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 8530
SECRET_KEY = b"AIORI_DNSSEC_SECRET_KEY_2026"
UPSTREAM_RESOLVER = os.getenv("UPSTREAM_RESOLVER", "127.0.0.1")

def resolve_domain(domain_name: str):
    """
    Simulates / performs DNSSEC resolution over upstream Unbound resolver.
    Status Codes:
      0 = SECURE (Authentic Data / AD flag verified)
      1 = BOGUS (Signature Invalid / Corrupted Zone)
    """
    if "bogus" in domain_name:
        # Invalid signature / Tampered record simulation
        return bytes([0, 0, 0, 0]), 1
    
    # Valid DNSSEC authenticated zone
    return bytes([192, 168, 1, 150]), 0

def start_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(5)
    print(f"[*] DNSSEC Gateway Proxy listening on {LISTEN_IP}:{LISTEN_PORT}...")

    while True:
        client_sock, addr = server.accept()
        try:
            data = client_sock.recv(1024)
            if not data:
                client_sock.close()
                continue
            
            domain = data.decode('utf-8').strip()
            print(f"[*] Processing query for domain: '{domain}' from {addr}")
            
            ip_bytes, status_code = resolve_domain(domain)
            
            # Payload Header = 4 Bytes IPv4 + 1 Byte Status Code = 5 Bytes Total
            payload_header = ip_bytes + bytes([status_code])
            
            # Compute 32-Byte HMAC-SHA256 Token over the exact 5-byte header
            token = hmac.new(SECRET_KEY, payload_header, hashlib.sha256).digest()
            
            # Binary Frame = 5 Bytes Header + 32 Bytes HMAC = 37 Bytes Total
            response_frame = payload_header + token
            client_sock.sendall(response_frame)
            print(f"[*] Successfully sent 37-byte authenticated frame to {addr}")
            
        except Exception as e:
            print(f"[!] Error handling client {addr}: {e}")
        finally:
            client_sock.close()

if __name__ == "__main__":
    start_proxy()
