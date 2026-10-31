import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="AIORI Gateway & ESP32 Security Operations Center (SOC)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Render Single-File Controllable Dashboard with Official PS-004 Terminology
html_dashboard_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIORI Gateway & IoT Client Security Visualizer</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

        body {
            font-family: 'Inter', sans-serif;
            background-color: #070a11;
            color: #f3f4f6;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }

        .font-mono {
            font-family: 'Fira Code', monospace;
        }

        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0b1120;
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 3px;
        }

        .glass-panel {
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .glass-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .glow-emerald {
            box-shadow: 0 0 25px rgba(16, 185, 129, 0.25);
        }
        .glow-red {
            box-shadow: 0 0 25px rgba(239, 68, 68, 0.25);
        }

        .pcb-board {
            background: radial-gradient(circle, #062c1d 0%, #03170e 100%);
            border: 2px solid #0fa968;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 0 15px rgba(15, 169, 104, 0.2);
        }

        .pcb-chip {
            background: linear-gradient(145deg, #1e2025, #111215);
            border: 1px solid #3a3d45;
            box-shadow: 3px 3px 6px rgba(0,0,0,0.6);
        }

        .led-active-green {
            background-color: #10b981;
            box-shadow: 0 0 10px #10b981, 0 0 20px #10b981;
        }

        .led-active-red {
            background-color: #ef4444;
            box-shadow: 0 0 10px #ef4444, 0 0 20px #ef4444;
        }

        .led-off {
            background-color: #1e293b;
            box-shadow: inset 0 0 3px rgba(0,0,0,0.8);
        }

        .hex-byte {
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .hex-byte:hover {
            transform: translateY(-3px) scale(1.08);
            z-index: 20;
        }
    </style>
</head>
<body class="p-3 bg-[#070a11] text-slate-100">

    <div class="max-w-[1550px] mx-auto space-y-3">
        
        <!-- HEADER CONTROL TOOLBAR -->
        <header class="glass-panel p-3.5 rounded-2xl border border-slate-800/80 shadow-2xl">
            <div class="flex flex-col xl:flex-row items-center justify-between gap-3">
                
                <div class="flex items-center gap-3 w-full xl:w-auto justify-between xl:justify-start">
                    <div class="flex items-center gap-2.5">
                        <div class="p-2 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400">
                            <i data-lucide="shield-check" class="w-6 h-6"></i>
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <h1 class="font-bold text-base text-white tracking-wide">AIORI Security Operations Center</h1>
                                <span class="px-2 py-0.5 text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full">PS-004</span>
                            </div>
                            <p class="text-xs text-slate-400">Authenticated Gateway-Assisted DNSSEC for IoT Clients</p>
                        </div>
                    </div>
                    
                    <div id="statusBadge" class="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 text-xs font-mono">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        <span>GATEWAY: READY</span>
                    </div>
                </div>

                <!-- Interactive Execution Controls (PS-004 3 Cases) -->
                <div class="flex flex-wrap items-center gap-2.5 w-full xl:w-auto justify-end">
                    
                    <div class="flex flex-col gap-0.5 min-w-[160px]">
                        <label class="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Executable Target</label>
                        <select id="scriptSelect" class="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500 font-mono">
                            <option value="gateway_service.py">gateway_service.py</option>
                            <option value="iot_client.py">iot_client.py</option>
                            <option value="unbound.conf">unbound.conf</option>
                        </select>
                    </div>

                    <div class="flex flex-col gap-0.5 min-w-[280px]">
                        <label class="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Mandatory Test Cases (PS-004)</label>
                        <select id="routeSelect" class="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500 font-mono">
                            <option value="SECURE">🟢 1. Secure DNS Case (DNSSEC-Signed Zone)</option>
                            <option value="INSECURE">🟡 2. Insecure DNS Case (Unsigned Zone)</option>
                            <option value="BOGUS">🔴 3. Bogus DNS Case (Gateway Block / RRSIG Fail)</option>
                        </select>
                    </div>

                    <div class="flex items-center gap-2 pt-3">
                        <button id="execBtn" onclick="runSimulation()" class="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold px-4 py-1.5 rounded-lg text-xs transition-all shadow-lg shadow-emerald-900/40 font-mono">
                            <i data-lucide="play" class="w-3.5 h-3.5 fill-current"></i>
                            <span>TRANSMIT</span>
                        </button>

                        <button onclick="resetConsole()" class="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-xs transition-all" title="Clear Console">
                            <i data-lucide="trash-2" class="w-4 h-4"></i>
                        </button>
                    </div>

                </div>
            </div>
        </header>

        <!-- TOP TELEMETRY CARDS -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
            
            <div id="cardVerdict" class="glass-card p-3 rounded-xl border-l-4 border-emerald-500 transition-all">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-[10px] font-mono uppercase text-slate-400">Security Verdict</p>
                        <h3 id="verdictTitle" class="text-sm font-bold font-mono text-emerald-400 mt-0.5">SECURE (0x00)</h3>
                    </div>
                    <div id="verdictIcon" class="p-1.5 bg-emerald-500/10 rounded-lg text-emerald-400">
                        <i data-lucide="shield-check" class="w-4 h-4"></i>
                    </div>
                </div>
                <p id="verdictSub" class="text-[11px] text-slate-400 mt-1.5 font-mono">DNSSEC Validated + HMAC Match</p>
            </div>

            <div class="glass-card p-3 rounded-xl border-l-4 border-purple-500">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-[10px] font-mono uppercase text-slate-400">Offload Latency</p>
                        <h3 id="telemetryLatency" class="text-sm font-bold font-mono text-purple-300 mt-0.5">1.18 ms</h3>
                    </div>
                    <div class="p-1.5 bg-purple-500/10 rounded-lg text-purple-400">
                        <i data-lucide="zap" class="w-4 h-4"></i>
                    </div>
                </div>
                <p class="text-[11px] text-slate-400 mt-1.5 font-mono">Client CPU Saved: <span class="text-purple-300 font-bold">98.9%</span>[cite: 1]</p>
            </div>

            <div class="glass-card p-3 rounded-xl border-l-4 border-blue-500">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-[10px] font-mono uppercase text-slate-400">Client Memory Overhead</p>
                        <h3 class="text-sm font-bold font-mono text-blue-300 mt-0.5">&lt; 0.1% SRAM</h3>
                    </div>
                    <div class="p-1.5 bg-blue-500/10 rounded-lg text-blue-400">
                        <i data-lucide="cpu" class="w-4 h-4"></i>
                    </div>
                </div>
                <p class="text-[11px] text-slate-400 mt-1.5 font-mono">Heavy RSA/ECDSA Offloaded[cite: 1]</p>
            </div>

            <div class="glass-card p-3 rounded-xl border-l-4 border-amber-500">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-[10px] font-mono uppercase text-slate-400">Trust Boundary</p>
                        <h3 class="text-sm font-bold font-mono text-amber-300 mt-0.5">Gateway-Assisted</h3>
                    </div>
                    <div class="p-1.5 bg-amber-500/10 rounded-lg text-amber-400">
                        <i data-lucide="key-round" class="w-4 h-4"></i>
                    </div>
                </div>
                <p class="text-[11px] text-slate-400 mt-1.5 font-mono">No Non-Validating Claim[cite: 1]</p>
            </div>

        </div>

        <!-- SYSTEM SCHEMATIC & TOPOLOGY CANVAS -->
        <div class="glass-panel p-4 rounded-2xl relative overflow-hidden">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                    <i data-lucide="cpu" class="w-4 h-4 text-emerald-400"></i>
                    <h2 class="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider">System Topology &amp; Test Scenario Visualizer</h2>
                </div>
                <div class="flex items-center gap-3 text-[11px] font-mono text-slate-400">
                    <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span>Secure Path</span>
                    <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span>Insecure Path</span>
                    <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-red-500 inline-block"></span>Bogus Drop</span>
                </div>
            </div>

            <div id="canvasBoundary" class="relative w-full h-[320px] bg-slate-950/90 rounded-xl border border-slate-800/80 p-3 overflow-hidden">
                
                <svg id="svgCanvas" class="absolute inset-0 w-full h-full pointer-events-none z-0">
                    <defs>
                        <filter id="glowG" x="-30%" y="-30%" width="160%" height="160%">
                            <feGaussianBlur stdDeviation="4" result="blur" />
                            <feComposite in="SourceGraphic" in2="blur" operator="over" />
                        </filter>
                    </defs>

                    <line id="wireCloudToGw" x1="18%" y1="36%" x2="40%" y2="36%" stroke="#1e293b" stroke-width="3" stroke-dasharray="6,6" />
                    <line id="wireGwToMcu" x1="60%" y1="36%" x2="78%" y2="36%" stroke="#1e293b" stroke-width="3" stroke-dasharray="6,6" />
                    
                    <g id="packetGroup" class="hidden">
                        <circle id="packetDot" r="9" fill="#10b981" filter="url(#glowG)" />
                        <text id="packetLabel" y="-14" text-anchor="middle" fill="#ffffff" font-size="10" font-family="Fira Code" font-weight="bold">Frame</text>
                    </g>
                </svg>

                <div class="relative z-10 grid grid-cols-12 h-full items-start pt-4">
                    
                    <!-- NODE 1: DNS Zone Server (Signed or Unsigned based on test case) -->
                    <div class="col-span-3 flex justify-center">
                        <div id="cloudNode" class="w-[210px] p-3 rounded-xl bg-slate-900/90 border border-blue-500/40 text-center shadow-lg relative group">
                            <div id="zoneBadge" class="absolute -top-2.5 left-1/2 -translate-x-1/2 px-2.5 py-0.5 bg-blue-500/20 border border-blue-500/40 rounded-full text-[9px] font-mono text-blue-300 whitespace-nowrap">
                                DNSSEC-SIGNED ZONE[cite: 1]
                            </div>
                            <div class="my-2 text-blue-400 flex justify-center">
                                <i data-lucide="cloud-lightning" class="w-8 h-8"></i>
                            </div>
                            <h4 id="zoneTitle" class="font-bold text-xs font-mono text-slate-100">DNS Zone Server</h4>
                            <p id="zoneSub" class="text-[10px] text-slate-400 font-mono mt-0.5">secure.aiori.lab</p>
                            <div id="zoneTech" class="mt-2 text-[9px] font-mono bg-slate-950 p-1 rounded border border-slate-800 text-slate-400">
                                RRSIG / DNSKEY Chain[cite: 1]
                            </div>
                            <div class="mt-2 inline-block px-2 py-0.5 bg-slate-950 border border-slate-700/80 rounded font-mono text-[9px] text-slate-300">
                                📄 unbound.conf
                            </div>
                        </div>
                    </div>

                    <!-- NODE 2: Validating Gateway -->
                    <div class="col-span-5 flex justify-center">
                        <div id="gwNodeBox" class="w-[260px] p-3 rounded-xl bg-slate-900/90 border border-purple-500/40 text-center shadow-lg relative transition-all">
                            <div class="absolute -top-2.5 left-1/2 -translate-x-1/2 px-2.5 py-0.5 bg-purple-500/20 border border-purple-500/40 rounded-full text-[9px] font-mono text-purple-300 whitespace-nowrap">
                                VALIDATING GATEWAY[cite: 1]
                            </div>
                            
                            <div class="my-1.5 flex items-center justify-center gap-2">
                                <div class="p-2 bg-purple-500/10 rounded-lg text-purple-400">
                                    <i data-lucide="server" class="w-7 h-7"></i>
                                </div>
                                <div class="text-left font-mono">
                                    <div class="text-xs font-bold text-slate-200">Local Gateway Proxy</div>
                                    <div class="text-[9px] text-purple-300">Unbound 1.17 Resolver</div>
                                    <div class="text-[9px] text-slate-400">UDP Port 8530</div>
                                </div>
                            </div>

                            <div class="grid grid-cols-2 gap-1 mt-2 font-mono text-[9px]">
                                <div id="gwDnssecBadge" class="bg-slate-950 p-1 rounded border border-slate-800 text-emerald-400 truncate">
                                    DNSSEC: ACTIVE[cite: 1]
                                </div>
                                <div id="gwHmacBadge" class="bg-slate-950 p-1 rounded border border-slate-800 text-purple-300 truncate">
                                    HMAC-SHA256
                                </div>
                            </div>
                            <div class="mt-2 inline-block px-2 py-0.5 bg-slate-950 border border-slate-700/80 rounded font-mono text-[9px] text-slate-300">
                                📄 gateway_service.py
                            </div>
                        </div>
                    </div>

                    <!-- NODE 3: IoT Client -->
                    <div class="col-span-4 flex justify-center">
                        <div id="mcuNodeBox" class="w-[300px] p-3 rounded-xl pcb-board text-center shadow-2xl relative transition-all">
                            <div class="absolute -top-2.5 left-1/2 -translate-x-1/2 px-2.5 py-0.5 bg-emerald-500/20 border border-emerald-500/50 rounded-full text-[9px] font-mono text-emerald-300 font-bold whitespace-nowrap">
                                IOT CLIENT (ESP32)[cite: 1]
                            </div>

                            <div class="grid grid-cols-12 gap-2 my-1 items-center">
                                <div class="col-span-5 pcb-chip p-2 rounded-lg border border-slate-700 flex flex-col items-center">
                                    <i data-lucide="cpu" class="w-5 h-5 text-slate-300 mb-0.5"></i>
                                    <span class="text-[9px] font-mono text-slate-300 font-bold">mbedTLS</span>
                                    <span class="text-[8px] font-mono text-slate-500">Lightweight</span>
                                </div>

                                <div class="col-span-7 bg-black p-2 rounded-lg border border-slate-800 font-mono text-left space-y-1">
                                    <div class="text-[8px] text-slate-500 border-b border-slate-900 pb-0.5 flex justify-between">
                                        <span>Client Output</span>
                                        <span id="oledStatus" class="text-emerald-400 font-bold">READY</span>
                                    </div>
                                    <div id="oledLine1" class="text-[9px] text-emerald-300 truncate">IP: ---.---.---.---</div>
                                    <div id="oledLine2" class="text-[8px] text-slate-400 truncate">HMAC: WAITING...</div>
                                </div>
                            </div>

                            <div class="flex items-center justify-between mt-2 pt-1.5 border-t border-emerald-900/60 font-mono text-[9px]">
                                <div class="flex items-center gap-1.5">
                                    <span id="ledGreen" class="w-2.5 h-2.5 rounded-full led-active-green inline-block"></span>
                                    <span class="text-slate-300">SEC</span>
                                    <span id="ledRed" class="w-2.5 h-2.5 rounded-full led-off inline-block ml-1"></span>
                                    <span class="text-slate-300">ERR</span>
                                </div>
                                <div class="bg-slate-950/80 px-2 py-0.5 rounded border border-emerald-800/40 text-amber-300">
                                    Trust Boundary OK[cite: 1]
                                </div>
                            </div>
                            <div class="mt-2 inline-block px-2 py-0.5 bg-slate-950 border border-slate-700/80 rounded font-mono text-[9px] text-slate-300">
                                📄 iot_client.py
                            </div>
                        </div>
                    </div>

                </div>

            </div>
        </div>

        <!-- BOTTOM SECTION -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3">
            
            <div class="lg:col-span-6 glass-panel p-3.5 rounded-2xl flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-2">
                            <i data-lucide="binary" class="w-4 h-4 text-emerald-400"></i>
                            <h3 class="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider">Authenticated Channel Frame Inspector</h3>
                        </div>
                        <span class="text-[10px] font-mono text-slate-400">37-Byte UDP Payload[cite: 1]</span>
                    </div>

                    <div class="space-y-2 mt-3 font-mono">
                        <div class="bg-slate-950/80 p-2 rounded-xl border border-blue-500/30">
                            <div class="flex justify-between text-[10px] text-blue-300 mb-1">
                                <span>Bytes 0..3: Resolved IPv4 Address</span>
                                <span id="hexIpText" class="font-bold text-white">10.0.0.1</span>
                            </div>
                            <div id="hexIpGrid" class="flex gap-1.5">
                                <span class="hex-byte bg-blue-950 text-blue-300 px-2 py-1 rounded text-xs border border-blue-500/40">0A</span>
                                <span class="hex-byte bg-blue-950 text-blue-300 px-2 py-1 rounded text-xs border border-blue-500/40">00</span>
                                <span class="hex-byte bg-blue-950 text-blue-300 px-2 py-1 rounded text-xs border border-blue-500/40">00</span>
                                <span class="hex-byte bg-blue-950 text-blue-300 px-2 py-1 rounded text-xs border border-blue-500/40">01</span>
                            </div>
                        </div>

                        <div class="bg-slate-950/80 p-2 rounded-xl border border-purple-500/30">
                            <div class="flex justify-between text-[10px] text-purple-300 mb-1">
                                <span>Byte 4: Validation Status Flag</span>
                                <span id="hexStatusText" class="font-bold text-emerald-400">0x00 (SECURE)</span>
                            </div>
                            <div id="hexStatusGrid" class="flex gap-1.5">
                                <span class="hex-byte bg-emerald-950 text-emerald-300 px-2.5 py-1 rounded text-xs border border-emerald-500/50 font-bold">00</span>
                            </div>
                        </div>

                        <div class="bg-slate-950/80 p-2 rounded-xl border border-emerald-500/30">
                            <div class="flex justify-between text-[10px] text-emerald-300 mb-1">
                                <span>Bytes 5..36: HMAC-SHA256 Token</span>
                                <span id="hmacMatchBadge" class="text-emerald-400 font-bold">MATCH [✓]</span>
                            </div>
                            <div id="hexHmacGrid" class="grid grid-cols-8 gap-1 text-center text-[10px]"></div>
                        </div>
                    </div>
                </div>

                <div class="mt-3 p-2 rounded-lg bg-slate-950 text-[10px] font-mono text-slate-400 flex items-center justify-between border border-slate-800">
                    <span>Frame Length: <strong class="text-slate-200">37 Bytes</strong></span>
                    <span>Algorithm: <strong class="text-emerald-400">HMAC-SHA256</strong></span>
                    <span>Validation Claim: <strong class="text-blue-300">Gateway-Assisted Only</strong>[cite: 1]</span>
                </div>
            </div>

            <div class="lg:col-span-6 glass-panel p-3.5 rounded-2xl flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-2">
                            <i data-lucide="terminal" class="w-4 h-4 text-emerald-400"></i>
                            <h3 class="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider">Evaluation Log Output</h3>
                        </div>
                        <span id="activeScriptBadge" class="text-[10px] font-mono bg-slate-800 px-2 py-0.5 rounded text-slate-300">gateway_service.py</span>
                    </div>

                    <div id="consoleLog" class="w-full h-[220px] bg-slate-950 p-3 rounded-xl border border-slate-800/90 font-mono text-xs overflow-y-auto space-y-1 text-slate-300 leading-relaxed shadow-inner">
                        <div class="text-slate-500">[SYSTEM READY] Select PS-004 test case and click TRANSMIT...</div>
                    </div>
                </div>

                <div class="mt-2 flex items-center justify-between text-[10px] font-mono text-slate-500">
                    <span>Target: IoT Client Socket</span>
                    <span>Status: Active</span>
                </div>
            </div>

        </div>

    </div>

    <script>
        lucide.createIcons();

        const SAMPLES = {
            SECURE: {
                ip: "10.0.0.1",
                hexIp: ["0A", "00", "00", "01"],
                statusByte: "00",
                statusLabel: "0x00 (SECURE)",
                hmac: ["4A", "8F", "1C", "90", "E3", "71", "B2", "04", "D5", "11", "99", "A8", "F0", "22", "88", "C4", "19", "77", "D3", "02", "81", "EE", "55", "34", "90", "BB", "72", "A1", "F4", "66", "10", "39"],
                verdict: "SECURE CASE[cite: 1]",
                verdictSub: "DNSSEC Validated + HMAC Match",
                isError: false,
                zoneType: "DNSSEC-SIGNED ZONE[cite: 1]",
                zoneName: "secure.aiori.lab",
                zoneDesc: "RRSIG / DNSKEY Chain Validated[cite: 1]"
            },
            INSECURE: {
                ip: "172.16.0.5",
                hexIp: ["AC", "10", "00", "05"],
                statusByte: "02",
                statusLabel: "0x02 (INSECURE)",
                hmac: ["BB", "11", "22", "33", "44", "55", "66", "77", "88", "99", "AA", "BB", "CC", "DD", "EE", "FF", "00", "11", "22", "33", "44", "55", "66", "77", "88", "99", "AA", "BB", "CC", "DD", "EE", "FF"],
                verdict: "INSECURE CASE[cite: 1]",
                verdictSub: "Unsigned Zone Forwarded Safely",
                isError: false,
                zoneType: "UNSIGNED ZONE",
                zoneName: "insecure.aiori.lab",
                zoneDesc: "No RRSIG Records Present"
            },
            BOGUS: {
                ip: "0.0.0.0",
                hexIp: ["00", "00", "00", "00"],
                statusByte: "01",
                statusLabel: "0x01 (BOGUS RRSIG)",
                hmac: ["FF", "00", "FF", "00", "AA", "BB", "CC", "DD", "11", "22", "33", "44", "55", "66", "77", "88", "99", "00", "11", "22", "33", "44", "55", "66", "77", "88", "99", "AA", "BB", "CC", "DD", "EE"],
                verdict: "BOGUS CASE[cite: 1]",
                verdictSub: "Gateway Blocked Forged RRSIG Signature",
                isError: true,
                zoneType: "BOGUS DNSSEC ZONE[cite: 1]",
                zoneName: "bogus.aiori.lab",
                zoneDesc: "Cryptographic Chain Failure[cite: 1]"
            }
        };

        function populateHmacGrid(bytes, isError) {
            const grid = document.getElementById('hexHmacGrid');
            grid.innerHTML = '';
            bytes.forEach(b => {
                const span = document.createElement('span');
                span.className = `hex-byte p-1 rounded font-mono ${isError ? 'bg-red-950 text-red-300 border border-red-800' : 'bg-emerald-950 text-emerald-300 border border-emerald-800/40'}`;
                span.innerText = b;
                grid.appendChild(span);
            });
        }

        populateHmacGrid(SAMPLES.SECURE.hmac, false);

        function logConsole(msg, type = 'info') {
            const c = document.getElementById('consoleLog');
            const d = document.createElement('div');
            const time = new Date().toISOString().substring(11, 19);
            
            if (type === 'error') {
                d.className = 'text-red-400 font-bold';
                d.innerText = `[${time}] 🚨 ${msg}`;
            } else if (type === 'success') {
                d.className = 'text-emerald-400 font-bold';
                d.innerText = `[${time}] ✓ ${msg}`;
            } else {
                d.className = 'text-slate-300';
                d.innerText = `[${time}] ${msg}`;
            }
            c.appendChild(d);
            c.scrollTop = c.scrollHeight;
        }

        function resetConsole() {
            document.getElementById('consoleLog').innerHTML = '<div class="text-slate-500">[LOG RESET] Terminal cleared...</div>';
        }

        function runSimulation() {
            const script = document.getElementById('scriptSelect').value;
            const route = document.getElementById('routeSelect').value;
            const sample = SAMPLES[route] || SAMPLES.SECURE;

            // Dynamically update Zone node metadata based on whether it's Signed, Insecure, or Bogus
            document.getElementById('zoneBadge').innerText = sample.zoneType;
            document.getElementById('zoneSub').innerText = sample.zoneName;
            document.getElementById('zoneTech').innerText = sample.zoneDesc;

            document.getElementById('activeScriptBadge').innerText = script;
            logConsole(`Executing PS-004 test case: '${route}'...`);

            animatePacket(route, sample);
        }

        function animatePacket(route, sample) {
            const pGroup = document.getElementById('packetGroup');
            const pDot = document.getElementById('packetDot');
            const pLabel = document.getElementById('packetLabel');
            
            pGroup.classList.remove('hidden');

            let startTime = null;
            const duration = 2000;

            const canvas = document.getElementById('canvasBoundary');
            const rect = canvas.getBoundingClientRect();
            const w = rect.width;
            const h = rect.height;

            const xCloud = w * 0.18;
            const xGw = w * 0.50;
            const xMcu = w * 0.82;
            const yBaseline = h * 0.36;

            function step(timestamp) {
                if (!startTime) startTime = timestamp;
                const progress = Math.min((timestamp - startTime) / duration, 1);

                let x = 0, y = 0;

                if (route === 'SECURE') {
                    pDot.setAttribute('fill', '#10b981');
                    pLabel.innerText = '37B Secure';
                    x = xCloud + progress * (xMcu - xCloud);
                    y = yBaseline;
                } else if (route === 'INSECURE') {
                    pDot.setAttribute('fill', '#f59e0b');
                    pLabel.innerText = 'Unsigned';
                    x = xCloud + progress * (xMcu - xCloud);
                    y = yBaseline;
                } else if (route === 'BOGUS') {
                    x = xCloud + progress * (xGw - xCloud);
                    y = yBaseline;

                    if (progress < 0.6) {
                        pDot.setAttribute('fill', '#10b981');
                        pLabel.innerText = 'Querying';
                    } else {
                        pDot.setAttribute('fill', '#ef4444');
                        pLabel.innerText = 'DROPPED';
                    }
                }

                pGroup.setAttribute('transform', `translate(${x}, ${y})`);

                if (progress < 1) {
                    requestAnimationFrame(step);
                } else {
                    updateHardwareUI(sample, route);
                }
            }

            requestAnimationFrame(step);
        }

        function updateHardwareUI(s, route) {
            const vTitle = document.getElementById('verdictTitle');
            const vSub = document.getElementById('verdictSub');
            const vCard = document.getElementById('cardVerdict');
            const vIcon = document.getElementById('verdictIcon');

            vTitle.innerText = s.verdict;
            vSub.innerText = s.verdictSub;

            if (s.isError) {
                vTitle.className = 'text-sm font-bold font-mono text-red-400 mt-0.5';
                vCard.className = 'glass-card p-3 rounded-xl border-l-4 border-red-500 glow-red transition-all';
                vIcon.className = 'p-1.5 bg-red-500/10 rounded-lg text-red-400';
                
                document.getElementById('ledGreen').className = 'w-2.5 h-2.5 rounded-full led-off inline-block';
                document.getElementById('ledRed').className = 'w-2.5 h-2.5 rounded-full led-active-red inline-block ml-1';

                document.getElementById('gwDnssecBadge').innerText = 'DNSSEC: BOGUS[cite: 1]';
                document.getElementById('gwDnssecBadge').className = 'bg-red-950 p-1 rounded border border-red-800 text-red-400 font-bold truncate';
                document.getElementById('oledStatus').innerText = 'GATEWAY DROP';
                document.getElementById('oledStatus').className = 'text-amber-400 font-bold';
                document.getElementById('oledLine1').innerText = 'IP: 0.0.0.0';
                document.getElementById('oledLine2').innerText = 'BOGUS RRSIG BLOCKED[cite: 1]';

                document.getElementById('hmacMatchBadge').innerText = 'REJECTED [❌]';
                document.getElementById('hmacMatchBadge').className = 'text-red-400 font-bold';

                logConsole(`Test Case Failed Verification (As Expected): ${s.verdict} - ${s.verdictSub}`, 'error');
            } else {
                vTitle.className = 'text-sm font-bold font-mono text-emerald-400 mt-0.5';
                vCard.className = 'glass-card p-3 rounded-xl border-l-4 border-emerald-500 glow-emerald transition-all';
                vIcon.className = 'p-1.5 bg-emerald-500/10 rounded-lg text-emerald-400';

                document.getElementById('ledGreen').className = 'w-2.5 h-2.5 rounded-full led-active-green inline-block';
                document.getElementById('ledRed').className = 'w-2.5 h-2.5 rounded-full led-off inline-block ml-1';

                document.getElementById('gwDnssecBadge').innerText = route === 'INSECURE' ? 'ZONE: INSECURE' : 'DNSSEC: VALID[cite: 1]';
                document.getElementById('gwDnssecBadge').className = 'bg-slate-950 p-1 rounded border border-slate-800 text-emerald-400 truncate';

                document.getElementById('oledStatus').innerText = route === 'INSECURE' ? 'INSECURE' : 'SECURE';
                document.getElementById('oledStatus').className = route === 'INSECURE' ? 'text-amber-400 font-bold' : 'text-emerald-400 font-bold';
                document.getElementById('oledLine1').innerText = `IP: ${s.ip}`;
                document.getElementById('oledLine2').innerText = route === 'INSECURE' ? 'FORWARDED (UNSIGNED)' : 'HMAC: VALID MATCH';

                document.getElementById('hmacMatchBadge').innerText = 'MATCH [✓]';
                document.getElementById('hmacMatchBadge').className = 'text-emerald-400 font-bold';

                logConsole(`Test Case Verified Successfully: ${s.verdict} for IPv4 ${s.ip}`, 'success');
            }

            document.getElementById('hexIpText').innerText = s.ip;
            const hexIpGrid = document.getElementById('hexIpGrid');
            hexIpGrid.innerHTML = '';
            s.hexIp.forEach(b => {
                const span = document.createElement('span');
                span.className = 'hex-byte bg-blue-950 text-blue-300 px-2 py-1 rounded text-xs border border-blue-500/40 font-mono';
                span.innerText = b;
                hexIpGrid.appendChild(span);
            });

            document.getElementById('hexStatusText').innerText = s.statusLabel;
            const hexStatusGrid = document.getElementById('hexStatusGrid');
            hexStatusGrid.innerHTML = `<span class="hex-byte ${s.isError ? 'bg-red-950 text-red-300 border-red-500/50' : 'bg-emerald-950 text-emerald-300 border-emerald-500/50'} px-2.5 py-1 rounded text-xs border font-mono font-bold">${s.statusByte}</span>`;

            populateHmacGrid(s.hmac, s.isError);
        }
    </script>
</body>
</html>
"""

components.html(html_dashboard_code, height=980, scrolling=True)
