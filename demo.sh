#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GATEWAY_DIR="$SCRIPT_DIR/src/gateway"

echo "========================================================================"
echo "    AIORI HACKATHON (A3-PS004-TC093) - DNSSEC OFFLOADING EDGE DEMO"
echo "========================================================================"

# 1. Start Docker Containers Automatically
echo "[*] Initializing Edge Gateway Microservices (Unbound + Proxy)..."
cd "$GATEWAY_DIR"
docker-compose up -d --build > /dev/null 2>&1

# 2. Wait for Gateway Socket to Open
echo "[*] Waiting for Gateway to listen on port 8530..."
for i in {1..10}; do
    if nc -z 127.0.0.1 8530 2>/dev/null || (exec 3<>/dev/tcp/127.0.0.1/8530) 2>/dev/null; then
        echo " └── [✓] Gateway Port 8530 Active!"
        break
    fi
    sleep 1
done

cd "$SCRIPT_DIR"

# 3. Run Automated Threat Simulation Suite
echo ""
echo "[*] Executing Automated Threat Verification Suite..."
python3 attack_demo.py

echo "========================================================================"
echo " [✓] DEMO COMPLETE: GATEWAY ACTIVE & READY FOR INTERACTIVE CLIENTS"
echo "========================================================================"
