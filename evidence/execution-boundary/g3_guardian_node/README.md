# One-command local guardian node — Zelda profile

From the repository root:

```sh
./guardian-node start
```

This starts the existing bounded G3 authority as a persistent local Docker service. On Zelda it reuses the already installed Linux/ARM64 image, verifies its recorded image ID and thirteen engine-source digests, builds an immutable source image without downloads, and retains state in the dedicated `upt-guardian-node-state` volume.

The selected Docker context must name a local Unix socket and a Linux daemon. Every subsequent call explicitly selects that context. A fresh node starts without an automatic restart policy; persistence is enabled only after its authority is observed ready. Failed first-start cleanup stops only that node and retains its container, logs and state volume.

The protected capability is exactly **one authority-owned zero-byte marker**. It is a live local service with actual Linux UID separation, the existing HOLD/effect transaction and the existing confined fixed executor. It does not install machine-wide interception, create an independent custodian, or certify authentic subject-level protection.

## Controls

```sh
./guardian-node status
./guardian-node apply
./guardian-node hold
./guardian-node stop
```

`apply` requests the one fixed operation through the existing executor, with the observed authority UID/PID and its Landlock/seccomp restrictions. An admission/started record blocks repeat execution, including after restart. A committed HOLD remains in the database; this launcher has no clear-HOLD or reset-state command. `stop` retains the volume. No protected operation is requested merely by starting the service.

`./guardian-node restart` replaces this node's container using the current wrapper bundle while retaining its volume. Engine-commit changes require a reviewed migration; missing/corrupt/partially provisioned data never becomes fresh unheld state automatically.

`--json` gives the source commit, actual process/UID, HOLD state and observed marker inode properties. The status explicitly records same-administrator custody and the absence of whole-machine enforcement. Logs remain local.

## Deployment boundaries

- No network, exposed ports, existing-host directories or production systems are mounted.
- Read-only container filesystem; one dedicated Linux state volume; bounded CPU, memory and process count.
- Authority, executor and controller use distinct non-root UIDs. The local container supervisor retains only the capabilities needed to provision those identities and manage their lifecycle.
- The installed Docker administrator remains trusted and can replace state. No independent R4 acceptance is inferred.
- Existing G3 engine modules are copied unchanged. This wrapper changes neither protection mathematics nor the HOLD authority.

The current source baseline is `77d3b2d1823fc09458873a1f5f461d24d349d337`, the reviewed #649 composition including isolated `-I -S` child startup and the explicit child HOME. `engine-manifest.json` fixes the exact thirteen used modules. Their bytes must match the checkout. The launcher has no permissive source-mismatch fallback.

## Current launch evidence

On 18 November 2026 the package was started successfully in Zelda's local Linux/ARM64 Docker VM. Recovery first verified the old guardian volume was empty through a read-only mount, then replaced only the failed container while retaining that volume. No provisioned state was reset or migrated.

The live authority created the one fixed marker, a repeat was denied, and HOLD was committed at generation 2. An actual same-volume container replacement retained the HOLD, admission record and marker inode. A subsequent request was denied. The node remains running in HOLD. The [live observation](live-observation-2026-11-18.md) records exact source/image identities, the environment and the qualification that the post-HOLD denial is not an isolated HOLD-first causal control.

Docker Desktop's start-at-login setting was enabled and verified in its UI and settings file. The container uses `unless-stopped`. Only container replacement was exercised; host reboot, login recovery and a year of uptime have not been observed. The launcher still refuses automatic engine migration for provisioned state.

After a successful start, `unless-stopped` requests persistence when the local Docker engine runs. It cannot guarantee a year of availability through host shutdown, resource exhaustion, lost state or administrative interference. No machine-wide protection or independently administered custody follows from keeping this one service running.

## Local profile

The short command above is the intended interface. This profile targets Zelda's already installed base image. It is a working launch package for that recorded environment, with explicit capability scope and fail-closed initialization. No universal G3 certification is claimed.
