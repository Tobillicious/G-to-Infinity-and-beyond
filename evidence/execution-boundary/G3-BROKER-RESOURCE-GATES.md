# G3 bounded broker input — adversarial engineering milestone

**Status:** research hardening only; no universal protection or production deployment.

Before this change the public Unix-socket broker and the separate control
broker used `ThreadingMixIn` without any active connection limit; a client
that sent a partial request and never sent a newline could occupy a worker
indefinitely. This is an availability bypass even when Ed25519 and effect
authorization checks are sound.

The shared `BoundedThreadingMixIn` now reserves a worker slot **before**
spawning a handler thread and immediately closes overload connections.
Both broker handlers set a finite socket read timeout before reading any
JSON. The default research limits are 16 public connections, 8 control
connections, and 2 seconds per inbound read; caller-configured bounds are
limited to 1–128 simultaneous connections and 0.1–10 seconds read timeout.
Slots are released in `finally` even if a handler raises. Linux tests hold
two half-written connections, assert third-connection shedding, then prove
that normal requests resume after the deadlines on both sockets.

**Limits:** a timeout per blocking socket read is NOT a total wall-time
deadline for slow trickle attacks: attackers can drip bytes under the
read timeout until hitting the length bound. Queueing at the kernel
listen backlog and request CPU time also remain potential DoS vectors.
There is no host cgroup quota, process separation, network policy, ingress
rate limiting, end-to-end control-plane priority or independent
high-availability emergency stop. Root and inherited descriptor bypasses,
cross-resource crash atomicity, authenticated real rights/consent, and the
original six X3 actual-world predicates remain release gates. Bounded
threads cannot certify universal physical guardianship.

Next: enforce a *monotonic total request deadline* for all framed inputs,
then test slow-trickle connections. Move the emergency hold to a separate
privilege-restricted process and independently exercise bypass attempts
before any live deployment. No actual new effect types, signing secrets
or production services are introduced.
