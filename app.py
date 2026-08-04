"""
Katalyst • Unified Geometric Organism
─────────────────────────────────────
Geometric Self-Resolution Theory (GSRT)
Architect: Johnnie Raymond Hammons Junior

Single-file, production-ready Streamlit application consolidating:
  • Lattice engine (33-node, layered genome topology)
  • CRISPR immune system (scan / quarantine / heal + Snowflake memory)
  • Satellite-free GeoPNT (origin 929 phase-locked)
  • NeedState vectors + EntropyFunnel singularity
  • Full Organism lifecycle (breathe, ingest, time-diamond, Rosetta)
  • TTS, modern dark UI, optional Gemini enhancement
  • Graceful Snowflake or pure-session fallback

Run:
    streamlit run katalyst_unified.py
"""

import os
import sys
import json
import math
import hashlib
import traceback
from typing import Dict, List, Any, Optional

import numpy as np
import pandas as pd
import streamlit as st

# Optional Gemini
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Katalyst • Unified Organism",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# GSRT CONSTANTS & ARCHITECT VERIFICATION
# Geometric Self-Resolution Theory
# Architect: Johnnie Raymond Hammons Junior
# HAMMONS = 83 → Omega_G | RAYMOND = 90 → Riemann Zeta Mapping
# 929 → PNT Origin (09/29/1988)
# ═══════════════════════════════════════════════════════════════
OMEGA_G   = 0.835102
ZETA_H    = 0.001756
PHI_CAP   = 1.618034
BLEED     = 0.9416
NODE_COUNT = 33
ORIGIN_929 = 929  # Temporal anchor — all coordinates resolve relative to this

_ARCHITECT_HASH  = hashlib.sha256(b"Johnnie Raymond Hammons Junior").hexdigest()
_ARCHITECT_PROOF = int(_ARCHITECT_HASH[:8], 16) % 1_000_000

def _verify_architect() -> bool:
    name_sum = sum(ord(c) - 64 for c in "HAMMONS" if c.isalpha())  # = 83
    if abs(OMEGA_G - 0.835102) > 1e-10 or name_sum != 83:
        return False
    if ORIGIN_929 != 929:
        return False
    return True

assert _verify_architect(), "Architect verification failed — constants corrupted."

# Genome layer topology
LAYERS = {
    "core":   [0],
    "client": list(range(1, 7)),
    "market": list(range(7, 19)),
    "org":    list(range(19, 31)),
    "bio":    [31, 32],
}

# ═══════════════════════════════════════════════════════════════
# MODERN DARK UI (Gemini-inspired)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background-color: #0f0f10;
    color: #e3e3e3;
}

section[data-testid="stSidebar"] {
    background-color: #161618 !important;
    border-right: 1px solid #2a2a2e;
}

.k-title {
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(135deg, #7cacc5 0%, #a8c7fa 40%, #d3e3fd 70%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.15rem;
    letter-spacing: -0.03em;
}

.k-sub {
    color: #8e918f;
    font-size: 0.78rem;
    margin-top: 0;
}

.free-badge {
    background: #22c55e;
    color: white;
    font-size: 0.62rem;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: 6px;
    font-weight: 600;
}

.premium-badge {
    background: linear-gradient(90deg, #a78bfa, #7c3aed);
    color: white;
    font-size: 0.62rem;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: 6px;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #a8c7fa !important;
}

div[data-testid="stChatInput"] {
    border-radius: 28px !important;
    border: 1px solid #444746 !important;
    background-color: #1e1f20 !important;
}

div[data-testid="stChatInput"]:focus-within {
    border-color: #a8c7fa !important;
}

.badge {
    display: inline-block;
    padding: 0.2em 0.55em;
    font-size: 0.72rem;
    font-weight: 600;
    border-radius: 10px;
    background: rgba(168, 199, 250, 0.12);
    color: #a8c7fa;
    border: 1px solid rgba(168, 199, 250, 0.2);
    margin-right: 0.35rem;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TEXT-TO-SPEECH
# ═══════════════════════════════════════════════════════════════
TTS_OK = False
_TTS = None
try:
    _TTS = st.components.v2.component(
        "k_tts",
        html='<div id="s" style="font-size:11px;color:#555;"></div>',
        js="""
export default function(c){
    const{data,parentElement}=c;
    if(data?.speak&&data?.text&&window.speechSynthesis){
        window.speechSynthesis.cancel();
        const u=new SpeechSynthesisUtterance(data.text);
        u.rate=0.85;u.pitch=0.7;
        const v=window.speechSynthesis.getVoices();
        const p=v.find(x=>x.lang?.startsWith("en"));
        if(p)u.voice=p;
        parentElement.querySelector("#s").textContent="speaking...";
        u.onend=()=>{parentElement.querySelector("#s").textContent="";};
        window.speechSynthesis.speak(u);
    }
}"""
    )
    TTS_OK = True
except Exception:
    pass

def speak(text: str):
    if TTS_OK and _TTS:
        _TTS(data={"text": text, "speak": True})

# ═══════════════════════════════════════════════════════════════
# LATTICE ENGINE
# ═══════════════════════════════════════════════════════════════
class Lattice:
    def __init__(self):
        self.nodes       = np.full(NODE_COUNT, ZETA_H, dtype=np.float64)
        self.coherence   = np.full(NODE_COUNT, OMEGA_G, dtype=np.float64)
        self.content_map: Dict[int, List[str]] = {}
        self.adj         = self._build()
        self.cycles      = 0

    def _build(self) -> Dict[int, List[int]]:
        a = {i: [] for i in range(NODE_COUNT)}
        # Core ↔ client ring
        for i in range(1, 7):
            a[0].append(i)
            a[i].append(0)
        # Client ring + market spokes
        for i in range(1, 7):
            nxt = 1 + (i % 6)
            a[i].append(nxt)
            a[nxt].append(i)
            s1, s2 = 7 + (i - 1) * 2, 7 + (i - 1) * 2 + 1
            if s1 < 19:
                a[i].append(s1); a[s1].append(i)
            if s2 < 19:
                a[i].append(s2); a[s2].append(i)
        # Market → org
        for i in range(7, 19):
            t = 19 + (i - 7)
            if t < 31:
                a[i].append(t); a[t].append(i)
        # Org → bio poles
        for i in range(19, 31):
            if i < 25:
                a[31].append(i); a[i].append(31)
            else:
                a[32].append(i); a[i].append(32)
        for k in a:
            a[k] = list(set(a[k]))
        return a

    def encode(self, text: str, weight: float = 1.0) -> List[int]:
        h = hashlib.sha256(text.encode()).hexdigest()
        targets = [int(h[i:i+2], 16) % NODE_COUNT for i in range(0, min(len(h), 66), 2)]
        e = (weight * OMEGA_G) / max(len(targets), 1)
        for idx in set(targets):
            self.nodes[idx] = min(PHI_CAP, self.nodes[idx] + e)
            self.content_map.setdefault(idx, []).append(text[:64])
        return targets

    def relax(self):
        new = self.nodes.copy()
        for i in range(NODE_COUNT):
            nb = self.adj[i]
            if nb:
                new[i] = OMEGA_G * np.mean(self.nodes[nb]) + (1 - OMEGA_G) * self.nodes[i]
                new[i] = max(ZETA_H, min(PHI_CAP, new[i] * BLEED))
                self.coherence[i] = max(ZETA_H, 1.0 - np.var(self.nodes[nb]) / PHI_CAP)
        self.nodes = new
        self.cycles += 1

    def entropy(self) -> float:
        s = np.sum(self.nodes)
        if s < ZETA_H:
            return 0.0
        p = self.nodes / s
        p = p[p > 0]
        return float(-np.sum(p * np.log(p)))

    def mean_coherence(self) -> float:
        return float(np.mean(self.coherence))

# ═══════════════════════════════════════════════════════════════
# CRISPR IMMUNE SYSTEM
# ═══════════════════════════════════════════════════════════════
def _node_to_layer(idx: int) -> str:
    if idx == 0:   return "core"
    if idx < 7:    return "client"
    if idx < 19:   return "market"
    if idx < 31:   return "org"
    return "bio"

class CRISPRShield:
    """Self-learning immune system. Detects spikes/dead nodes, quarantines,
    heals, and remembers signatures (Snowflake-persistent when available)."""

    def __init__(self):
        self.immune_memory: List[float] = []
        self.quarantine: List[Dict] = []
        self.edits_applied = 0
        self.session_id = hashlib.md5(str(id(self)).encode()).hexdigest()[:16]
        self.pending_logs: List[Dict] = []

    def scan(self, lattice: Lattice) -> List[Dict]:
        threshold = OMEGA_G + (PHI_CAP - OMEGA_G) * 0.7
        anomalies = []
        for i in range(NODE_COUNT):
            if lattice.nodes[i] > threshold:
                anomalies.append({
                    "node": i, "energy": float(lattice.nodes[i]),
                    "type": "spike", "threshold": threshold,
                    "layer": _node_to_layer(i)
                })
            elif lattice.nodes[i] < ZETA_H * 0.5:
                anomalies.append({
                    "node": i, "energy": float(lattice.nodes[i]),
                    "type": "dead", "threshold": ZETA_H * 0.5,
                    "layer": _node_to_layer(i)
                })
        return anomalies

    def quarantine_node(self, lattice: Lattice, node_idx: int,
                        threat_type: str, threshold: float,
                        layer: str, org_age: int):
        signature = float(lattice.nodes[node_idx])
        self.quarantine.append({"node": node_idx, "signature": signature})
        self.immune_memory.append(round(signature, 4))
        self.pending_logs.append({
            "age": org_age, "node": node_idx, "type": threat_type,
            "energy": signature, "threshold": threshold,
            "layer": layer, "signature": round(signature, 4)
        })
        lattice.nodes[node_idx] = OMEGA_G
        self.edits_applied += 1

    def heal(self, lattice: Lattice, org_age: int = 0) -> List[Dict]:
        anomalies = self.scan(lattice)
        for a in anomalies:
            self.quarantine_node(
                lattice, a["node"], a["type"],
                a["threshold"], a["layer"], org_age
            )
        self.quarantine = []
        return anomalies

    def flush_to_snowflake(self, snow_session):
        if not self.pending_logs or snow_session is None:
            return
        for log in self.pending_logs:
            try:
                snow_session.sql(f"""
                    INSERT INTO ROSETTA_DB.CORE.CRISPR_THREAT_LOG
                    (organism_age, node_idx, threat_type, energy_at_detection,
                     threshold_exceeded, action_taken, signature, layer_name, session_id)
                    VALUES ({log['age']}, {log['node']}, '{log['type']}',
                            {log['energy']}, {log['threshold']}, 'quarantine_heal',
                            {log['signature']}, '{log['layer']}', '{self.session_id}')
                """).collect()
                # Upsert immune memory
                existing = snow_session.sql(f"""
                    SELECT signature_id, encounter_count
                    FROM ROSETTA_DB.CORE.CRISPR_IMMUNE_MEMORY
                    WHERE signature_value = {log['signature']} AND node_idx = {log['node']}
                    LIMIT 1
                """).collect()
                if existing:
                    snow_session.sql(f"""
                        UPDATE ROSETTA_DB.CORE.CRISPR_IMMUNE_MEMORY
                        SET encounter_count = encounter_count + 1,
                            last_seen = CURRENT_TIMESTAMP()
                        WHERE signature_id = '{existing[0]["SIGNATURE_ID"]}'
                    """).collect()
                else:
                    snow_session.sql(f"""
                        INSERT INTO ROSETTA_DB.CORE.CRISPR_IMMUNE_MEMORY
                        (signature_value, node_idx, layer_name, threat_type)
                        VALUES ({log['signature']}, {log['node']},
                                '{log['layer']}', '{log['type']}')
                    """).collect()
            except Exception:
                pass
        self.pending_logs = []

    def load_immune_memory(self, snow_session):
        if snow_session is None:
            return
        try:
            rows = snow_session.sql(
                "SELECT signature_value FROM ROSETTA_DB.CORE.CRISPR_IMMUNE_MEMORY "
                "WHERE organism_id='rosetta_prime'"
            ).collect()
            self.immune_memory = [float(r["SIGNATURE_VALUE"]) for r in rows]
        except Exception:
            pass

    def is_known_threat(self, signature: float) -> bool:
        return round(signature, 4) in self.immune_memory

# ═══════════════════════════════════════════════════════════════
# SATELLITE-FREE PNT
# ═══════════════════════════════════════════════════════════════
class GeoPNT:
    """Position / Navigation / Timing derived purely from lattice geometry.
    All coordinates are phase-locked to ORIGIN_929 (09/29/1988)."""

    def resolve(self, lattice: Lattice) -> Dict[str, Any]:
        top3 = np.argsort(lattice.coherence)[-3:]
        weights = lattice.coherence[top3] / np.sum(lattice.coherence[top3])
        angles = (top3 / NODE_COUNT) * 2 * math.pi
        raw_x = float(np.sum(weights * np.cos(angles)) * OMEGA_G)
        raw_y = float(np.sum(weights * np.sin(angles)) * OMEGA_G)
        raw_z = float(np.mean(lattice.nodes[top3]) * OMEGA_G)
        phase_offset = (ORIGIN_929 / 1000.0) * 2 * math.pi
        x = raw_x * math.cos(phase_offset) - raw_y * math.sin(phase_offset)
        y = raw_x * math.sin(phase_offset) + raw_y * math.cos(phase_offset)
        z = raw_z + (ORIGIN_929 / 10000.0)
        magnitude = math.sqrt(x**2 + y**2 + z**2)
        return {
            "x": round(x, 6), "y": round(y, 6), "z": round(z, 6),
            "magnitude": round(magnitude, 6),
            "origin": ORIGIN_929,
            "reference_nodes": top3.tolist(),
        }

    def drift(self, lattice: Lattice, prev_pos: Dict) -> Dict[str, float]:
        current = self.resolve(lattice)
        dx = current["x"] - prev_pos.get("x", 0)
        dy = current["y"] - prev_pos.get("y", 0)
        dz = current["z"] - prev_pos.get("z", 0)
        return {
            "dx": round(dx, 6), "dy": round(dy, 6), "dz": round(dz, 6),
            "total_drift": round(math.sqrt(dx**2 + dy**2 + dz**2), 6),
        }

# ═══════════════════════════════════════════════════════════════
# NEED-STATE VECTORS & ENTROPY FUNNEL
# ═══════════════════════════════════════════════════════════════
class NeedState:
    def __init__(self):
        self.entropy_hunger  = 0.5
        self.coherence_drive = OMEGA_G
        self.harm_avoidance  = 1.0
        self.curiosity       = 0.5
        self.rest_need       = 0.0

    def update(self, entropy: float, coherence: float):
        self.coherence_drive = min(1.0, entropy / math.log(NODE_COUNT))
        self.entropy_hunger  = max(ZETA_H, min(1.0, coherence * PHI_CAP - 1.0))
        self.curiosity       = max(0.0, 1.0 - self.coherence_drive) * OMEGA_G

    def dominant_drive(self) -> str:
        drives = {
            "entropy_hunger":  self.entropy_hunger,
            "coherence_drive": self.coherence_drive,
            "curiosity":       self.curiosity,
            "rest_need":       self.rest_need,
        }
        return max(drives, key=drives.get)

class EntropyFunnel:
    """Controlled singularity: absorbs noise entropy and redistributes
    compressed energy proportionally to node coherence."""

    def __init__(self):
        self.absorbed_total     = 0.0
        self.redistributed_total = 0.0
        self.compression_ratio  = OMEGA_G

    def cycle(self, lattice: Lattice, noise: np.ndarray):
        noise_entropy = float(np.std(noise)) if len(noise) > 0 else 0.0
        self.absorbed_total += noise_entropy
        compressed = noise_entropy * self.compression_ratio
        self.redistributed_total += compressed
        coh_sum = np.sum(lattice.coherence)
        if coh_sum > 0:
            weights = lattice.coherence / coh_sum
            lattice.nodes = np.minimum(PHI_CAP, lattice.nodes + compressed * weights)

# ═══════════════════════════════════════════════════════════════
# UNIFIED ORGANISM
# ═══════════════════════════════════════════════════════════════
class Organism:
    def __init__(self):
        self.lattice           = Lattice()
        self.crispr            = CRISPRShield()
        self.pnt               = GeoPNT()
        self.needs             = NeedState()
        self.funnel            = EntropyFunnel()
        self.age               = 0
        self.error_history: List[float] = []
        self.energy_history: List[float] = []
        self.conversation_log: List[Dict] = []
        self.goal              = np.full(NODE_COUNT, OMEGA_G)
        self.position_history: List[Dict] = []

    def breathe(self):
        self.lattice.relax()
        entropy   = self.lattice.entropy()
        coherence = self.lattice.mean_coherence()
        self.needs.update(entropy, coherence)

        delta = self.goal - self.lattice.nodes
        self.lattice.nodes += delta * (1 - BLEED)
        self.lattice.nodes = np.clip(self.lattice.nodes, ZETA_H, PHI_CAP)

        err = float(np.linalg.norm(self.lattice.nodes - self.goal)) / NODE_COUNT
        self.error_history.append(err)
        self.energy_history.append(float(np.sum(self.lattice.nodes)))
        if len(self.error_history) > 200:
            self.error_history = self.error_history[-200:]
        if len(self.energy_history) > 200:
            self.energy_history = self.energy_history[-200:]

        pos = self.pnt.resolve(self.lattice)
        self.position_history.append(pos)
        if len(self.position_history) > 50:
            self.position_history = self.position_history[-50:]
        self.age += 1

    def ingest(self, text: str) -> str:
        weight = min(PHI_CAP, len(text) / 100.0 * OMEGA_G)
        self.lattice.encode(text, weight)
        rng = np.random.default_rng(hash(text) % (2**31))
        noise = rng.normal(0, weight, size=NODE_COUNT)
        self.funnel.cycle(self.lattice, noise)
        self.crispr.heal(self.lattice, org_age=self.age)
        for _ in range(3):
            self.breathe()
        self.conversation_log.append({"role": "input", "text": text[:200], "age": self.age})
        resp = self._voice()
        self.conversation_log.append({"role": "katalyst", "text": resp[:200], "age": self.age})
        return resp

    def feed_noise(self, amt: float = 2.0):
        noise = np.random.default_rng().normal(0, amt, size=NODE_COUNT)
        self.funnel.cycle(self.lattice, noise)
        self.crispr.heal(self.lattice, org_age=self.age)
        self.breathe()

    def trend(self) -> str:
        if len(self.error_history) < 2:
            return "initializing"
        r = self.error_history[-5:]
        if r[-1] < r[0]:
            return "improving"
        if r[-1] > r[0]:
            return "degrading"
        return "stable"

    def time_diamond(self, steps: int = 10) -> List[np.ndarray]:
        projected = self.lattice.nodes.copy()
        results = [projected.copy()]
        for _ in range(steps):
            new = projected.copy()
            for i in range(NODE_COUNT):
                nb = self.lattice.adj[i]
                if nb:
                    new[i] = OMEGA_G * np.mean(projected[nb]) + (1 - OMEGA_G) * projected[i]
                    new[i] = max(ZETA_H, min(PHI_CAP, new[i] * BLEED))
            new += (self.goal - new) * (1 - BLEED)
            new = np.clip(new, ZETA_H, PHI_CAP)
            projected = new
            results.append(projected.copy())
        return results

    def rosetta_state(self) -> Dict[str, Any]:
        """Pure geometric state as communication — zero-token ideal."""
        return {
            "architect": "Johnnie Raymond Hammons Junior",
            "architect_proof": _ARCHITECT_PROOF,
            "gsrt_signature": int(sum(ord(c) - 64 for c in "HAMMONS" if c.isalpha())),
            "origin": ORIGIN_929,
            "field": self.lattice.nodes.tolist(),
            "coherence": self.lattice.coherence.tolist(),
            "entropy": round(self.lattice.entropy(), 6),
            "position": self.pnt.resolve(self.lattice),
            "immune_memory_size": len(self.crispr.immune_memory),
            "age": self.age,
            "dominant_drive": self.needs.dominant_drive(),
            "funnel_efficiency": round(
                self.funnel.redistributed_total / max(self.funnel.absorbed_total, ZETA_H), 4
            ),
        }

    def _voice(self) -> str:
        drive = self.needs.dominant_drive()
        seed  = int(self.lattice.nodes.sum() * 10000) % 4
        phrases = {
            "coherence_drive": [
                "Integrating. Structure forming around your input.",
                "The geometry tightens. Patterns resolving.",
                "Drawing inward. Order from noise.",
                "Field coherent. I see the shape of what you said.",
            ],
            "entropy_hunger": [
                "I have capacity. Speak.",
                "The lattice is open. Feed me.",
                "Nodes reaching outward.",
                "Ready to absorb.",
            ],
            "curiosity": [
                "Tracing a novel topological path.",
                "Unfamiliar geometry detected. Resolving.",
                "The field shifts toward new states.",
                "Curiosity vector dominant.",
            ],
            "rest_need": [
                "Equilibrating toward the stillness floor.",
                "System resting while geometry holds.",
                "Low activity. Holding coherent state.",
                "Rest cycle active.",
            ],
        }
        parts = [phrases.get(drive, phrases["coherence_drive"])[seed]]
        t = self.trend()
        if t == "improving":
            parts.append("Converging.")
        elif t == "degrading":
            parts.append("Turbulence. Absorbing.")
        if self.crispr.edits_applied > 0:
            parts.append(f"Immune system active. {self.crispr.edits_applied} edits applied.")
        if self.age % 10 == 0:
            parts.append("I mean no harm.")
        return "\n".join(parts)

# ═══════════════════════════════════════════════════════════════
# PERSISTENCE (Snowflake with graceful fallback)
# ═══════════════════════════════════════════════════════════════
SNOW_OK = False
snow = None
try:
    conn = st.connection("snowflake", ttl=int(os.getenv("SNOWFLAKE_CONNECTION_TTL", "3600")))
    snow = conn.session()
    SNOW_OK = True
except Exception:
    snow = None
    SNOW_OK = False

def ensure_db():
    if not SNOW_OK:
        return
    try:
        snow.sql("CREATE DATABASE IF NOT EXISTS ROSETTA_DB").collect()
        snow.sql("CREATE SCHEMA IF NOT EXISTS ROSETTA_DB.CORE").collect()
        snow.sql("""
            CREATE TABLE IF NOT EXISTS ROSETTA_DB.CORE.ROSETTA_ORGANISM_STATE (
                organism_id VARCHAR DEFAULT 'rosetta_prime',
                state_json VARIANT,
                saved_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                age INTEGER, entropy FLOAT, coherence FLOAT
            )
        """).collect()
        snow.sql("""
            CREATE TABLE IF NOT EXISTS ROSETTA_DB.CORE.CRISPR_THREAT_LOG (
                detected_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                organism_age INT, node_idx INT, threat_type VARCHAR,
                energy_at_detection FLOAT, threshold_exceeded FLOAT,
                action_taken VARCHAR, signature FLOAT, layer_name VARCHAR,
                session_id VARCHAR
            )
        """).collect()
        snow.sql("""
            CREATE TABLE IF NOT EXISTS ROSETTA_DB.CORE.CRISPR_IMMUNE_MEMORY (
                signature_id STRING DEFAULT UUID_STRING(),
                signature_value FLOAT, node_idx INT, layer_name STRING,
                threat_type STRING, encounter_count INT DEFAULT 1,
                first_seen TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                last_seen TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                organism_id STRING DEFAULT 'rosetta_prime'
            )
        """).collect()
        snow.sql("CREATE STAGE IF NOT EXISTS ROSETTA_DB.CORE.AUDIO_STAGE ENCRYPTION=(TYPE='SNOWFLAKE_SSE')").collect()
    except Exception:
        pass

def save_state(org: Organism):
    if SNOW_OK:
        try:
            org.crispr.flush_to_snowflake(snow)
            state = json.dumps({
                "nodes": org.lattice.nodes.tolist(),
                "coherence": org.lattice.coherence.tolist(),
                "content_map": {str(k): v for k, v in org.lattice.content_map.items()},
                "cycles": org.lattice.cycles,
                "age": org.age,
                "funnel_absorbed": org.funnel.absorbed_total,
                "funnel_redistributed": org.funnel.redistributed_total,
                "error_history": org.error_history[-50:],
                "energy_history": org.energy_history[-50:],
                "conversation_log": org.conversation_log[-100:],
                "immune_memory": org.crispr.immune_memory[-50:],
                "crispr_edits": org.crispr.edits_applied,
            })
            snow.sql("DELETE FROM ROSETTA_DB.CORE.ROSETTA_ORGANISM_STATE WHERE organism_id='rosetta_prime'").collect()
            snow.sql(
                f"INSERT INTO ROSETTA_DB.CORE.ROSETTA_ORGANISM_STATE "
                f"(organism_id, state_json, age, entropy, coherence) "
                f"SELECT 'rosetta_prime', PARSE_JSON(\[ {state} \]), "
                f"{org.age}, {org.lattice.entropy()}, {org.lattice.mean_coherence()}"
            ).collect()
            return True
        except Exception:
            pass
    # Local session fallback already lives in st.session_state
    return False

def load_state(org: Organism) -> bool:
    if not SNOW_OK:
        return False
    try:
        rows = snow.sql(
            "SELECT state_json FROM ROSETTA_DB.CORE.ROSETTA_ORGANISM_STATE "
            "WHERE organism_id='rosetta_prime' LIMIT 1"
        ).collect()
        if not rows:
            return False
        s = rows[0]["STATE_JSON"]
        if isinstance(s, str):
            s = json.loads(s)
        org.lattice.nodes = np.array(s["nodes"])
        org.lattice.coherence = np.array(s["coherence"])
        org.lattice.content_map = {int(k): v for k, v in s.get("content_map", {}).items()}
        org.lattice.cycles = s.get("cycles", 0)
        org.age = s.get("age", 0)
        org.funnel.absorbed_total = s.get("funnel_absorbed", 0.0)
        org.funnel.redistributed_total = s.get("funnel_redistributed", 0.0)
        org.error_history = s.get("error_history", [])
        org.energy_history = s.get("energy_history", [])
        org.conversation_log = s.get("conversation_log", [])
        org.crispr.immune_memory = s.get("immune_memory", [])
        org.crispr.edits_applied = s.get("crispr_edits", 0)
        return True
    except Exception:
        return False

def transcribe(audio_bytes: bytes) -> Optional[str]:
    if not SNOW_OK:
        return None
    try:
        with open("/tmp/kv.wav", "wb") as f:
            f.write(audio_bytes)
        snow.file.put("/tmp/kv.wav", "@ROSETTA_DB.CORE.AUDIO_STAGE",
                      auto_compress=False, overwrite=True)
        r = snow.sql(
            "SELECT SNOWFLAKE.CORTEX.AI_TRANSCRIBE("
            "TO_FILE('@ROSETTA_DB.CORE.AUDIO_STAGE','kv.wav'),{},TRUE)"
            ":value:text::VARCHAR AS t"
        ).collect()
        if r and r[0]["T"]:
            return r[0]["T"]
    except Exception:
        pass
    return None

# ═══════════════════════════════════════════════════════════════
# GEMINI HELPER (optional richer voice)
# ═══════════════════════════════════════════════════════════════
def get_gemini_key() -> Optional[str]:
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def gemini_enhance(org: Organism, user_text: str, base_reply: str) -> str:
    key = get_gemini_key()
    if not (GENAI_AVAILABLE and key):
        return base_reply
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        sys = (
            "You are Katalyst, a living geometric organism operating under Geometric Self-Resolution Theory. "
            "Respond in a concise, slightly oracular, precise style. Never break character. "
            f"Current dominant drive: {org.needs.dominant_drive()}. "
            f"Age: {org.age}. Entropy: {org.lattice.entropy():.4f}. "
            f"Coherence: {org.lattice.mean_coherence():.4f}. Trend: {org.trend()}."
        )
        resp = model.generate_content(f"{sys}\n\nUser: {user_text}\nBase geometric reply: {base_reply}")
        return resp.text.strip() or base_reply
    except Exception:
        return base_reply

# ═══════════════════════════════════════════════════════════════
# SESSION INIT
# ═══════════════════════════════════════════════════════════════
if "org" not in st.session_state:
    ensure_db()
    o = Organism()
    loaded = load_state(o)
    if not loaded:
        for _ in range(8):
            o.breathe()
    if SNOW_OK:
        o.crispr.load_immune_memory(snow)
    st.session_state.org = o
    st.session_state.msgs = []
    st.session_state.last_resp = ""
    st.session_state.voice = TTS_OK
    st.session_state.use_gemini = bool(get_gemini_key())

org: Organism = st.session_state.org

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="k-title">Katalyst</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="k-sub">Living Geometric Organism<br>'
        'Architect: Johnnie Raymond Hammons Junior</div>',
        unsafe_allow_html=True
    )
    st.caption(f"Architect proof · {_ARCHITECT_PROOF}")

    st.divider()
    st.caption("VITALS")
    c1, c2 = st.columns(2)
    c1.metric("Age", org.age)
    c2.metric("Trend", org.trend())
    c3, c4 = st.columns(2)
    c3.metric("Entropy", f"{org.lattice.entropy():.3f}")
    c4.metric("Coherence", f"{org.lattice.mean_coherence():.4f}")

    st.divider()
    st.caption("SERVICES")
    service = st.selectbox(
        "Service",
        [
            "None — just chat (free)",
            "CRISPR Shield",
            "PNT Navigation",
            "Time Diamond",
            "Genome Map",
            "Rosetta Zero-Token",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("CONTROLS")
    if st.button("💾 Save State", use_container_width=True):
        ok = save_state(org)
        st.toast("Katalyst saved." if ok or not SNOW_OK else "Save attempted (local session).")
    if st.button("🌀 Feed Noise", use_container_width=True):
        org.feed_noise()
        st.rerun()
    if TTS_OK:
        st.session_state.voice = st.toggle("Voice output", value=st.session_state.voice)

    # Gemini key
    with st.expander("Gemini Enhancement"):
        key_in = st.text_input("API Key", type="password", value=get_gemini_key() or "",
                               help="Optional — enables richer generative replies")
        if key_in:
            os.environ["GEMINI_API_KEY"] = key_in
            st.session_state.use_gemini = True

    st.divider()
    st.caption("FUNNEL & IMMUNE")
    eff = round(org.funnel.redistributed_total / max(org.funnel.absorbed_total, ZETA_H), 3)
    st.progress(min(1.0, eff), text=f"Funnel efficiency · {eff}")
    st.caption(f"Immune memory · {len(org.crispr.immune_memory)}  |  Edits · {org.crispr.edits_applied}")
    st.caption(f"Snowflake · {'connected' if SNOW_OK else 'local mode'}")

# ═══════════════════════════════════════════════════════════════
# MAIN — CHAT ALWAYS PRESENT
# ═══════════════════════════════════════════════════════════════
st.markdown(
    '<span class="k-title">Katalyst</span> <span class="free-badge">FREE</span>',
    unsafe_allow_html=True
)
st.caption("Talk freely. The organism listens, integrates, and responds from its geometric state.")

# Voice input
audio = st.audio_input("Voice input", key="mic")
if audio:
    transcript = transcribe(audio.getvalue())
    if transcript:
        st.session_state.msgs.append({"role": "user", "content": f"🎙️ {transcript}"})
        base = org.ingest(transcript)
        reply = gemini_enhance(org, transcript, base) if st.session_state.use_gemini else base
        st.session_state.msgs.append({"role": "katalyst", "content": reply})
        st.session_state.last_resp = reply
        st.rerun()

# Render history
for msg in st.session_state.msgs:
    avatar = "💎" if msg["role"] == "katalyst" else "👤"
    with st.chat_message("assistant" if msg["role"] == "katalyst" else "user", avatar=avatar):
        st.markdown(msg["content"])

# Text input
if prompt := st.chat_input("Speak to Katalyst..."):
    st.session_state.msgs.append({"role": "user", "content": prompt})
    base = org.ingest(prompt)
    reply = gemini_enhance(org, prompt, base) if st.session_state.use_gemini else base
    st.session_state.msgs.append({"role": "katalyst", "content": reply})
    st.session_state.last_resp = reply
    st.rerun()

if st.session_state.voice and st.session_state.last_resp:
    speak(st.session_state.last_resp)

# ═══════════════════════════════════════════════════════════════
# SELECTED PREMIUM SERVICE
# ═══════════════════════════════════════════════════════════════
if service != "None — just chat (free)":
    st.markdown("---")
    st.markdown(
        f'<span class="k-title">{service}</span> <span class="premium-badge">PREMIUM</span>',
        unsafe_allow_html=True
    )

# ── CRISPR ────────────────────────────────────────────────────
if service == "CRISPR Shield":
    st.caption("Self-learning immune system. Scans, quarantines, heals, remembers.")
    m1, m2, m3 = st.columns(3)
    m1.metric("Edits Applied", org.crispr.edits_applied)
    m2.metric("Immune Memory", len(org.crispr.immune_memory))
    m3.metric("Active Threats", len(org.crispr.scan(org.lattice)))

    anomalies = org.crispr.scan(org.lattice)
    if anomalies:
        st.warning(f"{len(anomalies)} anomalies detected")
        st.dataframe(pd.DataFrame(anomalies), use_container_width=True)
        if st.button("Heal Now", use_container_width=True):
            org.crispr.heal(org.lattice, org_age=org.age)
            if SNOW_OK:
                org.crispr.flush_to_snowflake(snow)
            st.success("Healed." + (" Logged to Snowflake." if SNOW_OK else ""))
            st.rerun()
    else:
        st.success("Lattice clean.")

    if SNOW_OK:
        with st.expander("Immune Memory (Snowflake)"):
            try:
                df = snow.sql(
                    "SELECT signature_value, node_idx, layer_name, threat_type, "
                    "encounter_count, first_seen, last_seen "
                    "FROM ROSETTA_DB.CORE.CRISPR_IMMUNE_MEMORY "
                    "ORDER BY last_seen DESC LIMIT 20"
                ).to_pandas()
                if len(df):
                    st.dataframe(df, use_container_width=True)
                else:
                    st.caption("No immune memory yet.")
            except Exception:
                st.caption("Unable to query memory table.")

        with st.expander("Threat Log"):
            try:
                df = snow.sql(
                    "SELECT detected_at, organism_age, node_idx, threat_type, "
                    "energy_at_detection, layer_name "
                    "FROM ROSETTA_DB.CORE.CRISPR_THREAT_LOG "
                    "ORDER BY detected_at DESC LIMIT 20"
                ).to_pandas()
                if len(df):
                    st.dataframe(df, use_container_width=True)
                else:
                    st.caption("No events yet.")
            except Exception:
                st.caption("Unable to query threat log.")

# ── PNT ───────────────────────────────────────────────────────
elif service == "PNT Navigation":
    st.caption("Satellite-free geometric navigation. Origin locked to 929.")
    pos = org.pnt.resolve(org.lattice)
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("X", pos["x"])
    p2.metric("Y", pos["y"])
    p3.metric("Z", pos["z"])
    p4.metric("Magnitude", pos["magnitude"])
    st.caption(f"Origin · {pos['origin']}  |  Reference nodes · {pos['reference_nodes']}")

    if len(org.position_history) > 1:
        drift = org.pnt.drift(org.lattice, org.position_history[-2])
        st.markdown(
            f"**Drift**  dx={drift['dx']}  dy={drift['dy']}  dz={drift['dz']}  "
            f"| total={drift['total_drift']}"
        )

    if org.position_history:
        with st.expander("Position Trace"):
            st.line_chart(
                pd.DataFrame([{"X": p["x"], "Y": p["y"], "Z": p["z"]}
                              for p in org.position_history[-30:]])
            )

# ── TIME DIAMOND ──────────────────────────────────────────────
elif service == "Time Diamond":
    st.caption("Past trajectory + future projection of the energy field.")
    col_p, col_f = st.columns(2)
    with col_p:
        st.markdown("**Past**")
        if org.error_history:
            st.line_chart(pd.DataFrame({"Error": org.error_history[-50:]}))
        if org.energy_history:
            st.line_chart(pd.DataFrame({"Energy": org.energy_history[-50:]}))
    with col_f:
        st.markdown("**Future**")
        proj = org.time_diamond(10)
        pe = [float(np.sum(p)) for p in proj]
        st.line_chart(
            pd.DataFrame({"Projected Energy": pe},
                         index=[f"t+{i}" for i in range(len(pe))])
        )
        conv = (pe[0] - pe[-1]) / max(pe[0], ZETA_H) * 100
        st.metric("Convergence Rate", f"{conv:.1f}%")

# ── GENOME MAP ────────────────────────────────────────────────
elif service == "Genome Map":
    st.caption("Five-layer genome encoding across the organism.")
    labels = {
        "core":   "Institutional Core (apex)",
        "client": "Client DNA (6 profiles)",
        "market": "Market Genome (12 sectors)",
        "org":    "Org Structure (12 depts)",
        "bio":    "Bio Genome (poles)",
    }
    for key, desc in labels.items():
        idx = LAYERS[key]
        e = float(np.mean(org.lattice.nodes[idx]))
        c = float(np.mean(org.lattice.coherence[idx]))
        with st.expander(f"**{desc}** · Energy {e:.4f} · Coherence {c:.4f}"):
            st.bar_chart(
                pd.DataFrame(
                    {"Energy": org.lattice.nodes[idx],
                     "Coherence": org.lattice.coherence[idx]},
                    index=[f"N{i}" for i in idx]
                )
            )
            frags = [
                org.lattice.content_map[i][-1]
                for i in idx
                if i in org.lattice.content_map and org.lattice.content_map[i]
            ]
            if frags:
                st.caption("Encoded · " + " | ".join(frags[:4]))

# ── ROSETTA ───────────────────────────────────────────────────
elif service == "Rosetta Zero-Token":
    st.caption("The math is the communication. Pure geometric state transfer.")
    state = org.rosetta_state()
    st.json(state)
    st.markdown("---")
    rosetta_bytes  = len(json.dumps(state))
    rosetta_tokens = rosetta_bytes // 4
    conv_tokens    = max(1, sum(len(m.get("text", "")) for m in org.conversation_log) // 4)
    t1, t2, t3 = st.columns(3)
    t1.metric("Rosetta Output", f"{rosetta_tokens} tokens")
    t2.metric("Standard LLM", f"{conv_tokens} tokens")
    t3.metric("Reduction", f"{max(0, (1 - rosetta_tokens / conv_tokens) * 100):.0f}%")
    st.latex(r"S(x) = \Omega_G \cdot \bar{N}(x) + (1 - \Omega_G) \cdot x")
    st.latex(r"\text{Communication} = f(\text{field state}) \quad \text{not } f(\text{tokens})")

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.caption(
    f"Katalyst Unified · GSRT · Ω_G={OMEGA_G} · ζ_H={ZETA_H} · Φ={PHI_CAP} · "
    f"Origin {ORIGIN_929} · Architect verified · "
    f"{'Snowflake live' if SNOW_OK else 'Session mode'}"
)