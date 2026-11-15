# G3 bounded broker input — adversarial engineering milestone

**Status:** research hardening only; no universal protection or production deployment.

Before this change the public Unix-socket broker and the separate control
broker used `ThreadingMixIn` without any active connection limit; a client
that sent a partial request and never sent a newline could occupy a worker
indefinitely. This is an availability bypass even when Ed25519 and effect
authorization checks are sound.

The shared `BoundedThreadingMixIn` now reserves a worker slot **before**
spawning a handler thread and immediately closes overload connections.
Both broker handlers use a strict framed-input reader with a **total
monotonic wall-time deadline**, independent of how frequently a client sends
more bytes. The 2-second default bounds request-read occupation in ordinary
host scheduling conditions; valid request size is separately bounded. The default research limits are 16 public connections, 8 control
connections, and 2 seconds per inbound read; caller-configured bounds are
limited to 1–128 simultaneous connections and 0.1–10 seconds read timeout.
Slots are released in `finally` even if a handler raises. Linux tests hold
two half-written connections, assert third-connection shedding, then prove
that normal requests resume after the deadlines on both sockets.

**Limits:** this now includes a total request-read deadline, and the
adversarial tests also drip partial bytes faster than a per-read timeout
would fire. Queueing at the kernel listen backlog and CPU time for
processing complete requests remain potential DoS vectors.
There is no host cgroup quota, process separation, network policy, ingress
rate limiting, end-to-end control-plane priority or independent
high-availability emergency stop. Root and inherited descriptor bypasses,
cross-resource crash atomicity, authenticated real rights/consent, and the
original six X3 actual-world predicates remain release gates. Bounded
threads cannot certify universal physical guardianship.

Next: move the emergency hold to a separate privilege-restricted process,
add per-identity rate limits and independent resource quotas, then exercise
bypass attempts
before any live deployment. No actual new effect types, signing secrets
or production services are introduced.
