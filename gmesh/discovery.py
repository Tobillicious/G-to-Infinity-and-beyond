"""Local network peer discovery via UDP multicast.

Beacons are broadcast every few seconds on a multicast group.
Any node on the same local network hears them and maintains a peer list.
No internet required. No configuration required.
"""
import json
import socket
import struct
import threading
import time

MULTICAST_GROUP = "239.73.83.1"
MULTICAST_PORT = 31415
BEACON_INTERVAL = 5
PEER_TIMEOUT = 20


class Discovery:
    def __init__(self, node_id, http_port, manifest_sha, evidence_summary):
        self.node_id = node_id
        self.http_port = http_port
        self.manifest_sha = manifest_sha
        self.evidence_summary = evidence_summary
        self.peers = {}
        self._lock = threading.Lock()
        self._running = False

    def _local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _beacon_payload(self):
        return json.dumps({
            "node_id": self.node_id,
            "ip": self._local_ip(),
            "port": self.http_port,
            "manifest_sha": self.manifest_sha,
            "theorems": self.evidence_summary.get("total_theorems", 0),
            "sorry": self.evidence_summary.get("total_sorry", 0),
            "ts": time.time(),
        }).encode()

    def _send_beacons(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        while self._running:
            try:
                sock.sendto(self._beacon_payload(), (MULTICAST_GROUP, MULTICAST_PORT))
            except Exception:
                pass
            time.sleep(BEACON_INTERVAL)
        sock.close()

    def _listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass
        sock.bind(("", MULTICAST_PORT))

        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.settimeout(2.0)

        while self._running:
            try:
                data, addr = sock.recvfrom(4096)
                msg = json.loads(data.decode())
                peer_id = msg.get("node_id", addr[0])
                if peer_id == self.node_id:
                    continue
                with self._lock:
                    self.peers[peer_id] = {
                        "ip": msg.get("ip", addr[0]),
                        "port": msg.get("port"),
                        "manifest_sha": msg.get("manifest_sha"),
                        "theorems": msg.get("theorems"),
                        "sorry": msg.get("sorry"),
                        "last_seen": time.time(),
                    }
            except socket.timeout:
                pass
            except Exception:
                pass

            now = time.time()
            with self._lock:
                expired = [k for k, v in self.peers.items()
                           if now - v["last_seen"] > PEER_TIMEOUT]
                for k in expired:
                    del self.peers[k]

        sock.close()

    def get_peers(self):
        with self._lock:
            return dict(self.peers)

    def start(self):
        self._running = True
        threading.Thread(target=self._send_beacons, daemon=True).start()
        threading.Thread(target=self._listen, daemon=True).start()

    def stop(self):
        self._running = False
