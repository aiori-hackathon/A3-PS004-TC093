# A3-PS004-TC093: Authenticated Gateway-Assisted DNSSEC for IoT Clients

**Problem Statement ID:** PS-004  
**Category:** Cloud Computing & IoT  
**Event:** AIORI Hackathon 3  
**Team Code:** A3-PS004-TC093  

---

## 📹 Team Introduction Video

[![Team Introduction Video](https://img.youtube.com/vi/jABrWfCZKCs/maxresdefault.jpg)](https://youtu.be/jABrWfCZKCs)

> 🔗 **Video Link:** [Watch our Team Introduction & Problem Overview on YouTube](https://youtu.be/jABrWfCZKCs)

---

## 👥 Team & Mentorship Structure

### Faculty Project Guide
* **Dr. Vrushali Waghmare** – **Project Mentor & Academic Guide**
  * *Responsibility:* Architectural review, technical mentorship, research alignment, and validation of problem statement constraints.

### Student Team Members
* **Aditya Bhalekar** ([@Aditya93151](https://github.com/Aditya93151)) – **Project Lead & Core Systems Engineer**
  * *Email:* `bhalekaraditya9@gmail.com`
  * *Responsibility:* End-to-end design and implementation of the gateway-assisted offloading architecture, ESP32 MbedTLS client firmware development, BIND9/Unbound DNSSEC zone setup, HMAC authentication pipeline, benchmarking, and technical documentation.
* **Varun Gowda** ([@VarunG-99](https://github.com/VarunG-99)) – **Project Documentation & Asset Support**
  * *Responsibility:* Assisting with submission asset organization, repository upkeep, slide formatting verification, and presentation material review.

---

## 📌 Problem Overview & Proposed Solution

Resource-constrained microcontrollers (e.g., ESP32) lack the SRAM (~520 KB) and CPU budget required to parse multi-kilobyte DNSSEC signature chains (`RRSIG`, `DNSKEY`). Forcing local client validation leads to heap allocation failures, battery exhaustion, and packet fragmentation.

Our proposed **Authenticated Gateway-Assisted DNSSEC Offloading Architecture** delegates DNSSEC validation to a trusted local Edge Gateway running a validating resolver (Unbound/BIND9). Communication between the IoT client and gateway is secured over an authenticated TLS/HMAC channel:
* **Offloaded Heavy Compute:** Gateway handles upstream recursive `RRSIG` validation and checks the `AD` (Authentic Data) flag.
* **Lightweight Client Check:** The client verifies a single symmetric HMAC token/TLS session, achieving a **~90% reduction in RAM usage** and **~97% faster resolution time** while remaining protected against local DNS spoofing and cache poisoning.

---

## 📊 Benchmarking & Impact Matrix

| Metric / Parameter | Baseline (Client DNSSEC Validation) | Optimized Gateway-Offloaded Architecture | Engineering Impact |
| :--- | :--- | :--- | :--- |
| **Client Memory (Heap Allocation)** | ~142 KB | ~14 KB | **90% RAM Savings** |
| **Client Execution Latency** | 680 ms | 18 ms | **97% Speedup** |
| **Inbound Network Payload** | 2,840 Bytes (Fragmented UDP) | 96 Bytes (Single TLS Frame) | **96% Overhead Reduction** |
| **Validation Point** | Heavy On-Device RSA Parsing | Edge Proxy + HMAC Token Verification | **Zero OOM / Heap Crash Risk** |

---

## 📂 Project Structure & Deliverables

```text
A3-PS004-TC093/
├── A3-PS004-TC093.pdf      # Official Proposal & Presentation Slide Deck
├── README.md               # Team Details, Roles, & Video Link
└── src/                    # Source Code Repository
    ├── gateway/            # Validating Unbound/BIND9 Proxy Engine (Python/C++)
    └── esp32_client/       # MbedTLS Microcontroller Firmware (C/C++)
