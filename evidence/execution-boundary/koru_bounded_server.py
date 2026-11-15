"""Bounded Linux Unix-socket worker mixin for G3 research brokers.

Both the public and controller broker must use this mixin to prevent an
unbounded Python thread per inbound connection. This is process-local load
shedding only, not network-wide DDoS protection or deployment isolation.
"""
import socketserver
import threading


class BoundedThreadingMixIn(socketserver.ThreadingMixIn):
    daemon_threads = True
    block_on_close = False

    def configure_bounds(self, *, max_connections=16, request_timeout=2.0):
        if (type(max_connections) is not int or
                not 1 <= max_connections <= 128 or
                type(request_timeout) not in (int, float) or
                not 0.1 <= request_timeout <= 10.0):
            raise ValueError("invalid bounded-server configuration")
        self.max_connections = max_connections
        self.request_timeout = float(request_timeout)
        self._connection_slots = threading.BoundedSemaphore(max_connections)

    def process_request(self, request, client_address):
        # Acquire BEFORE creating a worker; an attacker cannot force an
        # unbounded number of stalled Python handler threads.
        if not self._connection_slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self._connection_slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._connection_slots.release()
