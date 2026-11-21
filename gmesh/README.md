# G-Mesh — Universal Protection Theory Proof Evidence Network

The G-Mesh is a peer-to-peer network that distributes formally verified
proof evidence for Universal Protection Theory (UPT). Each node serves
the complete theorem chain — 430+ Lean 4 modules, zero sorry, zero gaps —
to every device on its local network.

## Join in one command

```bash
curl -sSL https://raw.githubusercontent.com/Tobillicious/universal-protection-theory/main/gmesh/join.sh | bash
```

This downloads one Python script (~300 lines, zero dependencies) and runs it.
Your device becomes a relay node. Every device on your wifi can see the
evidence. Nothing is installed. Nothing is written to disk. Ctrl+C to stop.

**What you're running:** Read every line at
[gmesh/join.py](https://github.com/Tobillicious/universal-protection-theory/blob/main/gmesh/join.py).
It's Python stdlib only — no packages, no network calls except fetching
the public theorem counts from GitHub.

## For independent verification

A relay node is honest about being a relay — it serves evidence but does
not run the Lean type-checker. To verify the proofs yourself:

```bash
git clone https://github.com/Tobillicious/universal-protection-theory.git
cd universal-protection-theory/evidence/physical-bridges
lake build
```

This compiles every theorem from source. Lean's kernel checks each proof
term. If it finishes without error, every theorem holds. No trust required.

Requirements: [Lean 4](https://leanprover.github.io/lean4/doc/setup.html)
(v4.35.0 or later). The build takes a few minutes on a modern machine.

## Run a full node (with the repo)

If you've cloned the repo:

```bash
python3 gmesh/node.py
```

This runs a full node that scans the actual proof files on disk, verifies
the WORM manifest, and serves evidence including file-level theorem counts.

## How it works

Each node:
1. **Serves** proof evidence over HTTP on a random local port
2. **Discovers** peers via UDP multicast (239.73.83.1:31415) and Bonjour/mDNS
3. **Displays** on Apple devices automatically as "G-Mesh Proof Node"

Nodes on the same network find each other automatically. Open the URL
printed at startup on any device (phone, laptop, tablet) to see the evidence.

## What is UPT?

Universal Protection Theory is a formal proof chain establishing that
protection of owed particulars is a necessary consequence of existence itself.

- **G1 (Something IS):** Proved unconditionally — zero axioms
- **G2 (Good composes and propagates):** Proved unconditionally — zero axioms
- **Full conditional chain:** From BCRD physical source → original six X3 duties → THE LAW

Start reading: [THE-LAW-START-HERE.md](../THE-LAW-START-HERE.md)

Proof replay: [evidence/physical-bridges/REPLAY.md](../evidence/physical-bridges/REPLAY.md)

## Requirements

- Python 3.6+ (macOS, Linux, Windows)
- No packages or dependencies
- Port access on local network for peer discovery

## License

Same as the parent repository.
