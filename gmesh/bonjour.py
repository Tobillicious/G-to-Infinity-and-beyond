"""Bonjour/mDNS service advertisement.

Registers the G-Mesh proof node as an HTTP service via macOS dns-sd.
Every Apple device on the network sees it automatically in Safari
and local network discovery. No action needed from the other device.

This is an OFFER, not an install. The device sees the service,
the person chooses to open it.
"""
import subprocess
import threading


class BonjourAdvertiser:
    def __init__(self, service_name, port):
        self.service_name = service_name
        self.port = port
        self._proc = None

    def start(self):
        self._proc = subprocess.Popen(
            ["dns-sd", "-R", self.service_name, "_http._tcp", "local", str(self.port), "path=/"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def stop(self):
        if self._proc:
            self._proc.terminate()
            self._proc.wait()
            self._proc = None
