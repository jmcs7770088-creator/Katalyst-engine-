# KATALYST Sovereign Terminal Kernel v5.0
> **Project IRR**: Satellite-Free Intrinsic Medium PNT Engine & Multi-Node Socket Mesh

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)

## Overview
KATALYST is an AI and Positioning, Navigation, and Timing (PNT) framework built to operate independently of space-based assets (GPS) or external RF signals. By analyzing localized topological strain relative to a zero-dimensional origin ($V_0$), KATALYST achieves satellite-free coordinate resolution while utilizing Collatz-style vector clamping to eliminate computational drift at the edge.

## Key Mathematical Invariants
- **Geometric Stability Constant ($\Omega_G$)**: `0.835102`
- **Torsion Drift Variable ($\zeta_H$)**: `0.001756`
- **Golden Ratio Anchor ($\Phi$)**: `1.618034`

## Quick Start Guide

### 1. Clone Repository & Setup Environment
```bash
git clone [https://github.com/](https://github.com/)<your-username>/katalyst-pnt-engine.git
cd katalyst-pnt-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
