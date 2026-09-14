import streamlit as st
import numpy as np
import math
import socket
import threading
import json
import time

# ==========================================
# UNIVERSAL GSRT / PROJECT IRR CONSTANTS
# ==========================================
OMEGA_G = 0.835102   # Geometric Stability Constant
ZETA_H  = 0.001756   # Torsion Drift Threshold
PHI     = 1.618034   # Golden Ratio Anchor
DEFAULT_PORT = 9090  # Default Multi-Node PNT TCP Port

# ==========================================
# MULTI-NODE SOCKET DAEMON CLASS
# ==========================================
class MultiNodeMesh:
    def __init__(self, host="0.0.0.0", port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.connected_nodes = []
        self.received_logs = []
        self._lock = threading.Lock()

    def start_server(self):
        if self.running:
            return
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            threading.Thread(target=self._listen_loop, daemon=True).start()
            self._log(f"[SYS] Socket daemon listening on {self.host}:{self.port}")
        except Exception as e:
            self._log(f"[ERR] Failed to start socket server: {e}")
            self.running = False

    def _listen_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                self._log(f"[NET] Node connected from {addr[0]}:{addr[1]}")
                with self._lock:
                    self.connected_nodes.append(addr)
                threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True).start()
            except Exception:
                break

    def _handle_client(self, client_sock, addr):
        with client_sock:
            while self.running:
                try:
                    data = client_sock.recv(4096)
                    if not data:
                        break
                    payload = json.loads(data.decode('utf-8'))
                    self._log(f"[RX from {addr[0]}] {payload}")
                except Exception:
                    break
        with self._lock:
            if addr in self.connected_nodes:
                self.connected_nodes.remove(addr)
        self._log(f"[NET] Node {addr[0]} disconnected.")

    def send_packet(self, target_ip, target_port, payload_dict):
        def _send():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3.0)
                s.connect((target_ip, int(target_port)))
                s.sendall(json.dumps(payload_dict).encode('utf-8'))
                s.close()
                self._log(f"[TX to {target_ip}:{target_port}] Packet successfully broadcasted.")
            except Exception as e:
                self._log(f"[TX ERR] Target {target_ip}:{target_port} unreachable -> {e}")
        threading.Thread(target=_send, daemon=True).start()

    def _log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        with self._lock:
            self.received_logs.append(f"[{timestamp}] {msg}")

# Initialize Global Socket Instance in Streamlit Session
if "mesh_node" not in st.session_state:
    st.session_state.mesh_node = MultiNodeMesh()

# ==========================================
# BMT SATELLITE-FREE PNT SOLVER ENGINE
# ==========================================
class BMTIntrinsicReceiver:
    def __init__(self):
        # 1+6 Nodal Array Geometry (60-degree radial offset vectors)
        self.nodes = {
            0: {"label": "Core Origin V0", "vector": np.array([0.0, 0.0, 0.0])},
            1: {"label": "+X Strain",      "vector": np.array([1.0, 0.0, 0.0])},
            2: {"label": "+Y Tension",     "vector": np.array([0.5, 0.866, 0.0])},
            3: {"label": "+Z Torsion",     "vector": np.array([-0.5, 0.866, 0.0])},
            4: {"label": "-Y Tension",     "vector": np.array([-1.0, 0.0, 0.0])},
            5: {"label": "-Z Torsion",     "vector": np.array([-0.5, -0.866, 0.0])},
            6: {"label": "-X Strain",      "vector": np.array([0.5, -0.866, 0.0])}
        }
        self.position_lock = np.array([0.0, 0.0, 0.0])
        self.stillness_floor = 0.0

    def process_transducer_telemetry(self, raw_signals):
        """
        Executes Collatz Mirror Kick-Back PNT calculation
        """
        raw_arr = np.array(raw_signals)
        mu = np.mean(raw_arr)
        variance = np.var(raw_arr)
        
        # Calculate Structural Drift Factor D
        D = math.sqrt(variance) * OMEGA_G
        
        mirror_triggered = False
        k_hat = np.array([0.0, 0.0, 1.0]) # Orthogonal mirror axis
        
        # Check against Torsion Threshold (zeta_H)
        if D > ZETA_H:
            mirror_triggered = True
            # Execute 90-degree vector shift and mirror reversion (E_n+1 = k_hat x E_n)
            vec_sum = np.sum(raw_arr) * k_hat
            corrected_vector = np.cross(k_hat, vec_sum)
            # Clamp to stillness floor F_c = 0 and clamp to Phi ratio
            self.position_lock += (corrected_vector / PHI) * OMEGA_G
            self.stillness_floor = 0.0
        else:
            # Absolute PNT coordinate resolution relative to V0
            self.position_lock += np.mean(raw_arr, axis=0) * OMEGA_G
            self.stillness_floor = D

        return {
            "drift_D": D,
            "threshold_zeta": ZETA_H,
            "mirror_reversion_executed": mirror_triggered,
            "resolved_3d_pnt": self.position_lock.tolist(),
            "stillness_floor_Fc": self.stillness_floor
        }

# ==========================================
# STREAMLIT USER INTERFACE
# ==========================================
st.set_page_config(page_title="KATALYST BMT Node Terminal", layout="wide")

st.title("⚡ KATALYST Sovereign Terminal Kernel v5.0")
st.markdown("### Project IRR: Satellite-Free Intrinsic Medium PNT Engine & Socket Mesh")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.header("🛰️ 1+6 Transducer PNT Solver")
    st.write("Calculates 3D position locks without satellite RF signals via local topological strain.")
    
    # Input sliders for the 6-axis transducer signals
    s1 = st.slider("Node 1: +X Strain", -2.0, 2.0, 0.12)
    s2 = st.slider("Node 2: +Y Tension", -2.0, 2.0, -0.05)
    s3 = st.slider("Node 3: +Z Torsion", -2.0, 2.0, 0.44)
    s4 = st.slider("Node 4: -Y Tension", -2.0, 2.0, 0.02)
    s5 = st.slider("Node 5: -Z Torsion", -2.0, 2.0, -0.15)
    s6 = st.slider("Node 6: -X Strain", -2.0, 2.0, 0.31)

    receiver = BMTIntrinsicReceiver()
    pnt_results = receiver.process_transducer_telemetry([[s1, 0, 0], [0, s2, 0], [0, 0, s3], [-s4, 0, 0], [0, -s5, 0], [0, 0, -s6]])

    st.subheader("Telemetry & PNT Coordinates")
    m1, m2, m3 = st.columns(3)
    m1.metric("Drift Factor (D)", f"{pnt_results['drift_D']:.6f}")
    m2.metric("Threshold (ζ_H)", f"{ZETA_H}")
    m3.metric("Mirror Kick-Back", "ACTIVE" if pnt_results["mirror_reversion_executed"] else "LOCKED")

    st.code(f"""
[X Coordinates]: {pnt_results['resolved_3d_pnt'][0]:.8f}
[Y Coordinates]: {pnt_results['resolved_3d_pnt'][1]:.8f}
[Z Coordinates]: {pnt_results['resolved_3d_pnt'][2]:.8f}
[Stillness Floor Fc]: {pnt_results['stillness_floor_Fc']}
    """, language="text")

with col_right:
    st.header("🌐 Multi-Node Socket Mesh Network")
    st.write("Stream PNT locks and Rosetta state vectors directly between server nodes.")
    
    mesh = st.session_state.mesh_node
    
    # Daemon Control
    if not mesh.running:
        if st.button("Start Local TCP Listener"):
            mesh.start_server()
            st.rerun()
    else:
        st.success(f"TCP Daemon Active on Port {mesh.port}")
    
    st.subheader("Transmit State to Remote Node")
    target_ip = st.text_input("Remote Node IP Address", "192.168.1.50")
    target_port = st.number_input("Remote Port", value=9090)
    
    if st.button("Broadcast PNT Telemetry Packet"):
        packet = {
            "source_node": socket.gethostname(),
            "rosetta_header": "KP1.BMT_PNT_LOCK",
            "pnt_coords": pnt_results['resolved_3d_pnt'],
            "drift_D": pnt_results['drift_D'],
            "timestamp": time.time()
        }
        mesh.send_packet(target_ip, target_port, packet)

    st.subheader("Network Live Stream Log")
    st.text_area("Console Output", value="\n".join(mesh.received_logs[-15:]), height=250)
