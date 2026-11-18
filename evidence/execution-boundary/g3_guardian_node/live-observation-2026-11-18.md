# Zelda local guardian — observed live execution

18 November 2026, Pacific/Auckland. This records an actual local launch and fixed-marker effect on Zelda. It is a bounded operational milestone toward G3; the target of every relevant actual effect and all original six duties remains unchanged.

## Source and environment

The launched package source is #652 commit `91c4a8e4d3ee0b40ef1dfa105ab837a5d92e0883`. Its thirteen engine/observer files are unchanged from #649 commit `77d3b2d1823fc09458873a1f5f461d24d349d337`. The local source check and in-container verification match the manifest.

- Bundle SHA-256: `3ca00f383e5e92717e4412922daf6d74cf8445ce40d90710da9251e1f637d1e5`.
- Image ID: `sha256:59b63744380e2fc80d0ad4cfd282856171834cdb70e446803c04b6777dfa56b7`.
- Linux VM kernel: `6.12.69-linuxkit`; architecture: `aarch64`.
- Python: `3.13.18`; cryptography: `46.0.4`; OpenSSL: `3.5.7`.
- Authority UID: 65533; executor UID: 65532; controller UID: 65530.

The [machine-readable observation](live-observation-2026-11-18.json) retains the measured results. It is a same-administrator local record, not an independent R7 acceptance signature or a complete loaded-object attestation.

## Empty-state recovery

The earlier container was failing at import before provisioning. It was stopped, and a pinned local image inspected the existing labelled volume through a read-only mount. The directory contained no entries. Only after that observation was the exact failed container removed. The named state volume was retained. The corrected package then initialized and reached readiness.

This is not an engine-state migration: there was no provisioned state to transform. The launcher still rejects an engine mismatch on a provisioned node. No HOLD, admission journal, key or database was cleared to obtain readiness. The exact one-off recovery source is retained as [an audit record](zelda-empty-first-start-20261118.py.txt); it is not the general installation interface.

## Observed sequence

| Action | Actual observation |
| --- | --- |
| Start corrected authority | Ready, generation 1, no marker and no admission record |
| Request fixed operation | `synthetic_effect_returned`, `ok: true`; actual zero-byte marker appeared under UID 65533 |
| Repeat request | `authority_denied`, `ok: false`; marker inode unchanged |
| Controller commits HOLD | `hold_recorded`, generation 2, held true |
| Replace container, retain volume | New container identity; generation 2, HOLD, admission record and marker identity retained |
| Request after replacement | `authority_denied`; held true and marker inode unchanged |

The retained marker has device 65025, inode 1022411, one link and zero bytes. Its identity stayed the same throughout these observations. The authority process is a distinct non-root principal in the Linux VM. Its namespace PID may be 13 in different containers; the different container identities, rather than PID alone, establish replacement here.

The successful operation retains its source's `synthetic_effect_returned` result name. The filesystem effect was real, while the protected workload is the fixed marker fixture. Neither its name nor physical occurrence establishes human/AI subject protection.

The admission had already been recorded before HOLD. Therefore the post-HOLD denial does not, by itself, isolate HOLD as the only sufficient denial cause. This observation establishes persistent committed HOLD and continued denial; it does not replace the separate HOLD-first controls in the reviewed source/CI.

## Persistence and present operating state

The node is running in HOLD with `unless-stopped`. Docker Desktop's start-at-login checkbox was enabled, applied and visibly verified; the settings file independently reads `AutoStart: true`. Host reboot/login behavior has not been exercised, and continuous availability through a year has not been observed. Host shutdown, sleep, administrative interference and shared-resource exhaustion remain outside that availability evidence.

The Docker UI also reported the installed Desktop version as no longer supported. No Desktop upgrade was performed during this launch. The measured image and Linux kernel above identify the actual environment used.

## Exact remaining G3 scope

This node mediates one authority-owned marker operation. It does not intercept the Mac's other file writes, application actions, network requests or physical consequences. Starting the node does not make those outside routes covered. The existing full-domain mathematical results still require faithful actual-event coverage and authentic original-six subject meanings at their stated types.

All of these remain false in the observation: whole-machine enforcement; complete actual-effect coverage; independently administered custody; authentic six-duty reflections; independent R7 acceptance; one-year uptime evidence; unconditional universal protection. A second process or UID on the same administered Docker host is not an independent custodian.

The supplied Three Proofs attachment was also compared by bytes with the previously reviewed author source. It is identical, SHA-256 `5ef14e5dd107c08c1c240462041086050d1e39b5c35fc07c21b99239a47e41d4`. No new mathematical proof or enlarged conclusion is claimed from its resubmission.
