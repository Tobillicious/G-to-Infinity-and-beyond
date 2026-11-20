"""HTTP proof evidence server.

Serves proof evidence, WORM integrity checks, and peer discovery
to any device with a browser. No authentication required — the
proofs are meant to be seen.
"""
import json
import socketserver
import threading
from http.server import BaseHTTPRequestHandler
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"


def make_handler(repo_root, manifest_fn, evidence_fn, peers_fn):

    class Handler(BaseHTTPRequestHandler):

        def do_GET(self):
            path = self.path.split("?")[0].rstrip("/") or "/"

            if path == "/":
                self._serve_index()
            elif path == "/manifest":
                self._json_response(manifest_fn())
            elif path == "/verify":
                self._json_response(manifest_fn())
            elif path == "/evidence":
                self._json_response(evidence_fn())
            elif path == "/peers":
                self._json_response(peers_fn())
            else:
                self.send_error(404)

        def _json_response(self, data):
            body = json.dumps(data, indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def _serve_index(self):
            ev = evidence_fn()
            worm = manifest_fn()
            peers = peers_fn()

            template = TEMPLATES_DIR / "index.html"
            if template.exists():
                html = template.read_text()
            else:
                html = _fallback_html()

            html = html.replace("{{THEOREMS}}", str(ev.get("total_theorems", "?")))
            html = html.replace("{{SORRY}}", str(ev.get("total_sorry", "?")))
            html = html.replace("{{MODULES}}", str(ev.get("module_count", "?")))
            html = html.replace("{{FILES_TRACKED}}", str(worm.get("manifest", {}).get("files_tracked", "?")))
            html = html.replace("{{MANIFEST_SHA}}", str(worm.get("manifest", {}).get("manifest_sha256", "?"))[:16] + "...")
            html = html.replace("{{WORM_STATUS}}", worm.get("status", "UNKNOWN"))
            html = html.replace("{{PEER_COUNT}}", str(len(peers)))
            html = html.replace("{{SPOT_PASSED}}", str(worm.get("spot_check", {}).get("passed", "?")))
            html = html.replace("{{SPOT_SAMPLED}}", str(worm.get("spot_check", {}).get("files_sampled", "?")))

            key_html = ""
            for kr in ev.get("key_results", []):
                status = "FOUND" if kr["present"] else "NOT FOUND"
                key_html += f'<tr><td>{kr["label"]}</td><td>{kr["description"]}</td><td>{status}</td></tr>\n'
            html = html.replace("{{KEY_RESULTS_ROWS}}", key_html)

            peer_html = ""
            for pid, pinfo in peers.items():
                url = f'http://{pinfo["ip"]}:{pinfo["port"]}'
                peer_html += f'<tr><td>{pid}</td><td><a href="{url}">{url}</a></td><td>{pinfo.get("theorems", "?")}</td></tr>\n'
            if not peer_html:
                peer_html = '<tr><td colspan="3">No peers discovered yet</td></tr>\n'
            html = html.replace("{{PEER_ROWS}}", peer_html)

            body = html.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            pass

    return Handler


def _fallback_html():
    return """<!doctype html><html><head><meta charset=utf-8>
<title>G-Mesh Proof Node</title></head><body>
<h1>G-Mesh Proof Evidence</h1>
<p>Theorems: {{THEOREMS}} | Sorry: {{SORRY}} | Modules: {{MODULES}}</p>
<p>WORM: {{FILES_TRACKED}} files tracked | Status: {{WORM_STATUS}}</p>
<p>Peers: {{PEER_COUNT}}</p>
</body></html>"""


class ProofServer:
    def __init__(self, repo_root, manifest_fn, evidence_fn, peers_fn, port=0):
        handler = make_handler(repo_root, manifest_fn, evidence_fn, peers_fn)
        self.httpd = socketserver.TCPServer(("", port), handler)
        self.httpd.allow_reuse_address = True
        self.port = self.httpd.server_address[1]

    def start(self):
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def stop(self):
        self.httpd.shutdown()
