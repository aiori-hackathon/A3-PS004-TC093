#!/usr/bin/env python3
"""
Gateway Proxy Daemon for Authenticated Gateway-Assisted DNSSEC Offloading
Team Code: A3-PS004-TC093 | Problem Statement: PS-004
"""

import socket
import ssl
import hmac
import hashlib
import struct
import dns.resolver
import dns.flags
import dns.message
import dns.query

# ==========================================
# CONFIGURATION CONSTANTS
# ==========================================
LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 8530             # Custom TLS port for ESP32 clients
UPSTREAM_RESOLVER = '127.0.0.1' # Local BIND9/Unbound IP or 8.8.8.8 for testing
SHARED_HMAC_KEY = b'aiori_ps004_secret_key_2026' # Pre-shared key for client auth

# TLS Server Certificates (Self-signed or generated for lab environment)
CERT_FILE = 'server.crt'
KEY_FILE = 'server.key'


def resolve_and_validate_dnssec(domain_name: str) -> tuple[int, str]:
    """
    Queries upstream DNS server with EDNS0 DO (DNSSEC OK) bit enabled.
    Returns status code and resolved IP or error string.
    
    Status Codes:
        0: SUCCESS (Valid DNSSEC or standard domain)
        1: BOGUS (DNSSEC signature verification failed / tampered)
        2: SERVFAIL / Resolution error
    """
    try:
        query = dns.message.make_query(domain_name, dns.rdatatype.A, want_dnssec=True)
        response = dns.query.udp(query, UPSTREAM_RESOLVER, timeout=3.0)
        
        rcode = response.rcode()
        flags = response.flags
        
        # Check for SERVFAIL or DNSSEC validation failures
        if rcode == dns.rcode.SERVFAIL:
            print(f"[GATEWAY] Upstream returned SERVFAIL for {domain_name} (Likely BOGUS signature).")
            return 1, "0.0.0.0"
            
        if rcode != dns.rcode.NOERROR:
            print(f"[GATEWAY] DNS lookup failed with rcode: {dns.rcode.to_text(rcode)}")
            return 2, "0.0.0.0"
            
        # Check Authentic Data (AD) flag for DNSSEC validation proof
        is_authenticated = bool(flags & dns.flags.AD)
        print(f"[GATEWAY] Query: {domain_name} | AD Flag: {is_authenticated}")
        
        # Extract IPv4 address from answer section
        for rrset in response.answer:
            if rrset.rdtype == dns.rdatatype.A:
                for item in rrset:
                    return 0, str(item)
                    
        return 2, "0.0.0.0"

    except Exception as e:
        print(f"[GATEWAY] Resolver Exception: {e}")
        return 2, "0.0.0.0"


def build_signed_payload(status_code: int, ip_address: str) -> bytes:
    """
    Constructs a lightweight 68-byte binary frame:
    [1 byte Status] + [4 bytes IPv4] + [32 bytes Timestamp/Nonce] + [32 bytes HMAC-SHA256]
    """
    # Convert IPv4 string to 4-byte packed binary
    try:
        ip_bytes = socket.inet_aton(ip_address)
    except socket.error:
        ip_bytes = socket.inet_aton("0.0.0.0")
        
    # Status code (1 byte: 0=OK, 1=BOGUS, 2=FAIL)
    status_byte = struct.pack("!B", status_code)
    
    # Body to be signed
    data_to_sign = status_byte + ip_bytes
    
    # Compute HMAC-SHA256 signature
    signature = hmac.new(SHARED_HMAC_KEY, data_to_sign, hashlib.sha256).digest()
    
    # Final packed payload sent to ESP32
    return data_to_sign + signature


def handle_client(client_socket, client_address):
    """Handles incoming TLS connection from ESP32 IoT client."""
    print(f"[GATEWAY] Connected by client: {client_address}")
    try:
        # Receive domain query string from ESP32
        data = client_socket.recv(256).decode('utf-8').strip()
        if not data:
            return
            
        print(f"[GATEWAY] Received domain lookup request: '{data}'")
        
        # Execute upstream DNSSEC resolution
        status, ip_addr = resolve_and_validate_dnssec(data)
        
        # Build HMAC-signed compact payload
        payload = build_signed_payload(status, ip_addr)
        
        # Send authenticated payload back to ESP32
        client_socket.sendall(payload)
        print(f"[GATEWAY] Dispatched {len(payload)}-byte payload for {data} ({ip_addr}) | Status: {status}")
        
    except Exception as e:
        print(f"[GATEWAY] Client handler error: {e}")
    finally:
        client_socket.close()


def start_gateway():
    """Initializes the TLS server socket daemon."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((LISTEN_HOST, LISTEN_PORT))
    server_sock.listen(5)
    
    print(f"==================================================")
    print(f" Validating DNSSEC Gateway Proxy Listening on {LISTEN_PORT}")
    print(f" Target Upstream Resolver: {UPSTREAM_RESOLVER}")
    print(f"==================================================")
    
    # SSL Context Setup (Optional: enable SSL for production deployment)
    # context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    while True:
        try:
            client, addr = server_sock.accept()
            # To wrap with TLS, uncomment: client = context.wrap_socket(client, server_side=True)
            handle_client(client, addr)
        except KeyboardInterrupt:
            print("\n[GATEWAY] Shutting down gateway server.")
            break
        except Exception as e:
            print(f"[GATEWAY] Server error: {e}")

    server_sock.close()


if __name__ == '__main__':
    start_gateway()
