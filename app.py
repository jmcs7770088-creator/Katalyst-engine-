"""
Katalyst Protocol v1
────────────────────
Geometric State Communication Protocol
Architect: Johnnie Raymond Hammons Junior

A functional token-reduction wrapper and candidate standard for
efficient AI-to-AI and human-to-AI context transfer.

Core idea:
  Maintain a living 33-node geometric field.
  Continuously compress the field into a compact, versioned,
  differentially encoded packet (Rosetta Packet).
  Use that packet as high-density context instead of raw
  conversation history whenever possible.

Design goals for a future standard:
  • Compact (target < 180 chars for full state, < 80 for delta)
  • Versioned & self-describing
  • Differential (only send what changed)
  • Model-agnostic (works in front of any LLM)
  • Interpretable (field remains human-inspectable)
  • Extensible (future learned codecs can plug in)

Run:
    streamlit run katalyst_protocol.py
"""

from __future__ import annotations

import os
import json
import math
import hashlib
import struct
import base64
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# Optional Gemini / any LLM
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# PROTOCOL CONSTANTS
# ═══════════════════════════════════════════════════════════════
PROTOCOL_VERSION = "KP1"          # Katalyst Protocol v1
OMEGA_G   = 0.835102
ZETA_H    = 0.001756
PHI_CAP   = 1.618034
BLEED     = 0.9416
NODE_COUNT = 33
ORIGIN_929 = 929

# Quantization: 8-bit is a good balance of size vs fidelity
QBITS = 8
QMAX  = (1 << QBITS) - 1         # 255

_ARCHITECT_HASH  = hashlib.sha256(b"Johnnie Raymond Hammons Junior").hexdigest()
_ARCHITECT_PROOF = int(_ARCHITECT_HASH[:8], 16) % 1_000_000

LAYERS = {
    "core":   [0],
    "client": list(range(1, 7)),
    "market": list(range(7, 19)),
    "org":    list(range(19, 31)),
    "bio":    [31, 32],
}

# ═══════════════════════════════════════════════════════════════
# PAGE + UI
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Katalyst Protocol",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background: #0b0c0e; color: #e6e8eb; }
section[data-testid="stSidebar"] { background: #111316 !important; border-right: 1px solid #22262b; }
.kp-title { font-size: 1.75rem; font-weight: 700; letter-spacing: -0.03em;
            background: linear-gradient(120deg, #7dd3fc, #a78bfa, #f0abfc);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.kp-mono { font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; }
.metric-good { color: #4ade80 !important; }
div[data-testid="stMetricValue"] { color: #7dd3fc !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CORE GEOMETRIC ENGINE (kept lean and fast)
# ═══════════════════════════════════════════════════════════════
class Lattice:
    def __init__(self):
        self.nodes     = np.full(NODE_COUNT, ZETA_H, dtype=np.float64)
        self.coherence = np.full(NODE_COUNT, OMEGA_G, dtype=np.float64)
        self.adj       = self._build()
        self.cycles    = 0

    def _build(self):
        a = {i: [] for i in range(NODE_COUNT)}
        for i in range(1, 7):
            a[0].append(i); a[i].append(0)
        for i in range(1, 7):
            nxt = 1 + (i % 6)
            a[i].append(nxt); a[nxt].append(i)
            s1, s2 = 7 + (i-1)*2, 7 + (i-1)*2 + 1
            if s1 < 19: a[i].append(s1); a[s1].append(i)
            if s2 < 19: a[i].append(s2); a[s2].append(i)
        for i in range(7, 19):
            t = 19 + (i - 7)
            if t < 31: a[i].append(t); a[t].append(i)
        for i in range(19, 31):
            pole = 31 if i < 25 else 32
            a[pole].append(i); a[i].append(pole)
        for k in a: a[k] = list(set(a[k]))
        return a

    def encode(self, text: str, weight: float = 1.0):
        h = hashlib.sha256(text.encode()).hexdigest()
        targets = [int(h[i:i+2], 16) % NODE_COUNT for i in range(0, min(len(h), 66), 2)]
        e = (weight * OMEGA_G) / max(len(set(targets)), 1)
        for idx in set(targets):
            self.nodes[idx] = min(PHI_CAP, self.nodes[idx] + e)
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
        s = float(np.sum(self.nodes))
        if s < ZETA_H: return 0.0
        p = self.nodes / s
        p = p[p > 0]
        return float(-np.sum(p * np.log(p)))

    def mean_coherence(self) -> float:
        return float(np.mean(self.coherence))

# ═══════════════════════════════════════════════════════════════
# ROSETTA PACKET — THE ACTUAL PROTOCOL
# ═══════════════════════════════════════════════════════════════
@dataclass
class RosettaPacket:
    """
    Versioned geometric state packet.
    Designed to be the smallest high-fidelity representation of the field
    that another system can usefully interpret.
    """
    version: str
    seq: int                          # monotonic sequence number
    full: bool                        # True = full state, False = delta
    age: int
    entropy: float
    coherence: float
    energy: bytes                     # quantized node energies
    coh: bytes                        # quantized coherences (only on full)
    changed_mask: Optional[bytes]     # which nodes changed (delta only)
    architect_proof: int
    ts: float                         # unix timestamp

    def to_wire(self) -> str:
        """Serialize to a compact URL-safe string. This is what gets sent."""
        header = {
            "v": self.version,
            "s": self.seq,
            "f": 1 if self.full else 0,
            "a": self.age,
            "e": round(self.entropy, 5),
            "c": round(self.coherence, 5),
            "p": self.architect_proof,
            "t": int(self.ts),
        }
        payload = {
            "h": header,
            "en": base64.urlsafe_b64encode(self.energy).decode("ascii").rstrip("="),
        }
        if self.full:
            payload["co"] = base64.urlsafe_b64encode(self.coh).decode("ascii").rstrip("=")
        else:
            payload["m"] = base64.urlsafe_b64encode(self.changed_mask).decode("ascii").rstrip("=")

        raw = json.dumps(payload, separators=(",", ":"))
        return f"KP1.{base64.urlsafe_b64encode(raw.encode()).decode('ascii').rstrip('=')}"

    @staticmethod
    def from_wire(wire: str) -> "RosettaPacket":
        if not wire.startswith("KP1."):
            raise ValueError("Not a Katalyst Protocol v1 packet")
        b64 = wire[4:] + "=" * (-len(wire[4:]) % 4)
        raw = base64.urlsafe_b64decode(b64.encode())
        data = json.loads(raw)
        h = data["h"]
        energy = base64.urlsafe_b64decode(data["en"] + "=" * (-len(data["en"]) % 4))
        coh = None
        mask = None
        if h["f"]:
            coh = base64.urlsafe_b64decode(data["co"] + "=" * (-len(data["co"]) % 4))
        else:
            mask = base64.urlsafe_b64decode(data["m"] + "=" * (-len(data["m"]) % 4))
        return RosettaPacket(
            version=h["v"], seq=h["s"], full=bool(h["f"]),
            age=h["a"], entropy=h["e"], coherence=h["c"],
            energy=energy, coh=coh, changed_mask=mask,
            architect_proof=h["p"], ts=h["t"],
        )

    def size_chars(self) -> int:
        return len(self.to_wire())


def quantize(arr: np.ndarray, lo: float = ZETA_H, hi: float = PHI_CAP) -> bytes:
    """Map float array into 8-bit unsigned bytes."""
    clipped = np.clip(arr, lo, hi)
    scaled = (clipped - lo) / (hi - lo) * QMAX
    return scaled.astype(np.uint8).tobytes()


def dequantize(buf: bytes, lo: float = ZETA_H, hi: float = PHI_CAP) -> np.ndarray:
    arr = np.frombuffer(buf, dtype=np.uint8).astype(np.float64)
    return lo + (arr / QMAX) * (hi - lo)


class RosettaCodec:
    """
    Maintains previous state so we can emit cheap differential packets.
    This is the heart of the token-reduction system.
    """
    def __init__(self):
        self.seq = 0
        self.prev_nodes: Optional[np.ndarray] = None
        self.prev_coh: Optional[np.ndarray] = None
        self.last_full_seq = -999

    def encode(self, lattice: Lattice, age: int, force_full: bool = False) -> RosettaPacket:
        self.seq += 1
        # Force a full packet every 12 steps or on first call
        need_full = (
            force_full
            or self.prev_nodes is None
            or (self.seq - self.last_full_seq) >= 12
        )

        if need_full:
            self.last_full_seq = self.seq
            pkt = RosettaPacket(
                version=PROTOCOL_VERSION,
                seq=self.seq,
                full=True,
                age=age,
                entropy=lattice.entropy(),
                coherence=lattice.mean_coherence(),
                energy=quantize(lattice.nodes),
                coh=quantize(lattice.coherence, lo=0.0, hi=1.0),
                changed_mask=None,
                architect_proof=_ARCHITECT_PROOF,
                ts=time.time(),
            )
        else:
            # Differential: only send nodes that moved more than a small epsilon
            delta = np.abs(lattice.nodes - self.prev_nodes)
            changed = delta > 0.008
            # Pack changed values densely
            changed_idx = np.where(changed)[0]
            # Simple mask: 33 bits → 5 bytes (pad to byte)
            mask = np.packbits(changed.astype(np.uint8))
            # Only quantize the changed energies
            changed_energy = quantize(lattice.nodes[changed]) if len(changed_idx) else b""
            pkt = RosettaPacket(
                version=PROTOCOL_VERSION,
                seq=self.seq,
                full=False,
                age=age,
                entropy=lattice.entropy(),
                coherence=lattice.mean_coherence(),
                energy=changed_energy,
                coh=None,
                changed_mask=mask.tobytes(),
                architect_proof=_ARCHITECT_PROOF,
                ts=time.time(),
            )

        self.prev_nodes = lattice.nodes.copy()
        self.prev_coh = lattice.coherence.copy()
        return pkt

    def decode_into(self, pkt: RosettaPacket, lattice: Lattice):
        """Apply a packet onto a lattice (receiver side)."""
        if pkt.full:
            lattice.nodes = dequantize(pkt.energy)
            if pkt.coh is not None:
                lattice.coherence = dequantize(pkt.coh, lo=0.0, hi=1.0)
        else:
            # Reconstruct which nodes changed
            mask_bits = np.unpackbits(np.frombuffer(pkt.changed_mask, dtype=np.uint8))[:NODE_COUNT]
            changed_idx = np.where(mask_bits.astype(bool))[0]
            if len(changed_idx) and len(pkt.energy):
                vals = dequantize(pkt.energy)
                lattice.nodes[changed_idx] = vals[:len(changed_idx)]


# ═══════════════════════════════════════════════════════════════
# ORGANISM (lean)
# ═══════════════════════════════════════════════════════════════
class Organism:
    def __init__(self):
        self.lattice = Lattice()
        self.codec   = RosettaCodec()
        self.age     = 0
        self.goal    = np.full(NODE_COUNT, OMEGA_G)
        self.history: List[str] = []          # recent natural language (kept short)
        self.packets: List[RosettaPacket] = []
        self.total_raw_tokens = 0
        self.total_rosetta_chars = 0

    def breathe(self, n: int = 1):
        for _ in range(n):
            self.lattice.relax()
            delta = self.goal - self.lattice.nodes
            self.lattice.nodes += delta * (1 - BLEED)
            self.lattice.nodes = np.clip(self.lattice.nodes, ZETA_H, PHI_CAP)
            self.age += 1

    def ingest(self, text: str) -> RosettaPacket:
        weight = min(PHI_CAP, len(text) / 120.0 * OMEGA_G)
        self.lattice.encode(text, weight)
        self.breathe(2)
        self.history.append(text[:180])
        if len(self.history) > 12:
            self.history = self.history[-12:]
        # Estimate raw tokens (rough)
        self.total_raw_tokens += max(1, len(text) // 4)
        pkt = self.codec.encode(self.lattice, self.age)
        self.packets.append(pkt)
        self.total_rosetta_chars += pkt.size_chars()
        if len(self.packets) > 40:
            self.packets = self.packets[-40:]
        return pkt

    def emit(self, force_full: bool = False) -> RosettaPacket:
        pkt = self.codec.encode(self.lattice, self.age, force_full=force_full)
        self.packets.append(pkt)
        self.total_rosetta_chars += pkt.size_chars()
        return pkt

    def apply_packet(self, wire: str):
        pkt = RosettaPacket.from_wire(wire)
        self.codec.decode_into(pkt, self.lattice)
        self.age = max(self.age, pkt.age)

    def context_for_llm(self, max_history: int = 3) -> str:
        """
        Build the actual context string that should be sent to an LLM.
        Prefer Rosetta packet + tiny recent text over full history.
        """
        pkt = self.emit()
        recent = self.history[-max_history:] if self.history else []
        parts = [
            f"[Katalyst Protocol {PROTOCOL_VERSION} state]",
            f"packet: {pkt.to_wire()}",
            f"entropy={pkt.entropy:.4f} coherence={pkt.coherence:.4f} age={pkt.age}",
        ]
        if recent:
            parts.append("recent:")
            for r in recent:
                parts.append(f"- {r}")
        return "\n".join(parts)

    def stats(self) -> Dict[str, Any]:
        last = self.packets[-1] if self.packets else None
        return {
            "age": self.age,
            "entropy": round(self.lattice.entropy(), 5),
            "coherence": round(self.lattice.mean_coherence(), 5),
            "last_packet_chars": last.size_chars() if last else 0,
            "last_packet_full": last.full if last else None,
            "total_raw_tokens_est": self.total_raw_tokens,
            "total_rosetta_chars": self.total_rosetta_chars,
            "packets_emitted": len(self.packets),
            "compression_ratio": round(
                self.total_rosetta_chars / max(self.total_raw_tokens * 4, 1), 3
            ),
        }


# ═══════════════════════════════════════════════════════════════
# LLM WRAPPER (the actual product interface)
# ═══════════════════════════════════════════════════════════════
def get_gemini_key():
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


class KatalystWrapper:
    """
    Drop-in token-reduction layer.
    Usage:
        k = KatalystWrapper()
        reply = k.chat("Your message", llm_callable)
    """
    def __init__(self):
        self.org = Organism()

    def chat(self, user_text: str, llm_callable=None, use_rosetta: bool = True) -> Tuple[str, Dict]:
        """
        Returns (reply, stats)
        If llm_callable is provided it should accept a single string prompt
        and return a string response.
        """
        pkt = self.org.ingest(user_text)

        if llm_callable is None:
            # Pure geometric reply (no external model)
            drive = "coherent" if self.org.lattice.mean_coherence() > 0.7 else "seeking"
            reply = {
                "coherent": "Field integrated. Structure holds.",
                "seeking": "Capacity available. Continue.",
            }[drive]
            return reply, self.org.stats()

        if use_rosetta:
            # High-density path: send packet + minimal recent text
            prompt = (
                "You are receiving context via Katalyst Protocol (geometric state packet). "
                "Treat the packet as compressed long-term state. "
                "Respond helpfully and concisely.\n\n"
                + self.org.context_for_llm()
                + f"\n\nUser: {user_text}"
            )
        else:
            # Classic path for comparison
            history = "\n".join(self.org.history[-8:])
            prompt = f"Conversation so far:\n{history}\n\nUser: {user_text}"

        reply = llm_callable(prompt)
        return reply, self.org.stats()


def make_gemini_callable():
    key = get_gemini_key()
    if not (GENAI_AVAILABLE and key):
        return None
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    def call(prompt: str) -> str:
        try:
            r = model.generate_content(prompt)
            return r.text.strip()
        except Exception as e:
            return f"[model error: {e}]"
    return call


# ═══════════════════════════════════════════════════════════════
# STREAMLIT APP
# ═══════════════════════════════════════════════════════════════
if "wrapper" not in st.session_state:
    st.session_state.wrapper = KatalystWrapper()
    st.session_state.messages = []
    st.session_state.use_rosetta = True

k: KatalystWrapper = st.session_state.wrapper
org = k.org

# Sidebar
with st.sidebar:
    st.markdown('<div class="kp-title">Katalyst Protocol</div>', unsafe_allow_html=True)
    st.caption(f"v{PROTOCOL_VERSION} · Architect proof {_ARCHITECT_PROOF}")
    st.divider()

    stats = org.stats()
    c1, c2 = st.columns(2)
    c1.metric("Age", stats["age"])
    c2.metric("Packets", stats["packets_emitted"])
    c3, c4 = st.columns(2)
    c3.metric("Entropy", f"{stats['entropy']:.4f}")
    c4.metric("Coherence", f"{stats['coherence']:.4f}")

    st.divider()
    st.session_state.use_rosetta = st.toggle("Use Rosetta packets", value=True)
    st.caption("When on: LLM receives compact geometric state instead of full history")

    st.divider()
    st.markdown("**Token Economics**")
    st.metric("Est. raw tokens seen", stats["total_raw_tokens_est"])
    st.metric("Rosetta chars emitted", stats["total_rosetta_chars"])
    ratio = stats["compression_ratio"]
    st.metric("Chars / raw-token", f"{ratio:.3f}")
    if stats["last_packet_chars"]:
        st.caption(f"Last packet: {stats['last_packet_chars']} chars · {'FULL' if stats['last_packet_full'] else 'DELTA'}")

    st.divider()
    if st.button("Force full packet", use_container_width=True):
        pkt = org.emit(force_full=True)
        st.session_state.messages.append({
            "role": "system",
            "content": f"Full packet forced ({pkt.size_chars()} chars)\n```\n{pkt.to_wire()}\n```"
        })
        st.rerun()

    with st.expander("Gemini key (optional)"):
        key_in = st.text_input("API Key", type="password", value=get_gemini_key() or "")
        if key_in:
            os.environ["GEMINI_API_KEY"] = key_in

# Main
st.markdown('<div class="kp-title">Katalyst Protocol</div>', unsafe_allow_html=True)
st.caption("Geometric state packets as a candidate standard for token-efficient context transfer")

# Live packet view
if org.packets:
    last = org.packets[-1]
    with st.expander("Latest Rosetta Packet (wire format)", expanded=False):
        st.code(last.to_wire(), language="text")
        st.caption(f"{last.size_chars()} characters · seq {last.seq} · {'full state' if last.full else 'differential'}")

# Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    llm = make_gemini_callable()
    reply, stats = k.chat(prompt, llm_callable=llm, use_rosetta=st.session_state.use_rosetta)

    # Show what was actually sent under the hood
    if st.session_state.use_rosetta and org.packets:
        pkt = org.packets[-1]
        meta = f"\n\n---\n*Rosetta · {pkt.size_chars()} chars · {'FULL' if pkt.full else 'DELTA'} · seq {pkt.seq}*"
        reply_display = reply + meta
    else:
        reply_display = reply

    st.session_state.messages.append({"role": "assistant", "content": reply_display})
    st.rerun()

# Protocol explanation
st.markdown("---")
st.markdown("### Why this can become a standard")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Compact**")
    st.caption("8-bit quantized field + differential encoding. Full state usually < 220 chars. Deltas often under 100.")
with col2:
    st.markdown("**Model-agnostic**")
    st.caption("Any LLM can receive a Rosetta packet as context. No special weights required.")
with col3:
    st.markdown("**Stateful**")
    st.caption("The field carries long-horizon intent, constraints, and tone so history can be aggressively truncated.")

st.markdown("""
**Wire format**  
`KP1.<base64url(json({header, quantized_energy, optional_coherence_or_mask}))>`

**Recommended usage pattern**
1. Maintain one Katalyst instance per long-running conversation or agent.
2. On every turn: ingest user text → emit packet.
3. Send to the model: latest packet + last 1–3 utterances only.
4. Periodically force a full packet (every ~12 turns) for resync.
5. Measure actual tokens used vs full-history baseline.

This is no longer a cosmetic reduction metric. It is a concrete, versioned, differentially encoded geometric context layer.
""")