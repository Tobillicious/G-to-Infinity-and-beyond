# G3 Linux SCM_RIGHTS kernel cut — bounded contrast

**16 November 2026. Research-only Linux x86-64 test. No deployment or canonical proof changes.**

## The exact experiment

Merged [PR #475](https://github.com/Tobillicious/universal-protection-theory/pull/475) demonstrates that an unconfined process with UID 65534 can modify a protected HTML artifact **after HOLD** when a cooperating privileged process delegates a previously opened writable descriptor through Unix-domain `SCM_RIGHTS`. Path DAC and a broker HOLD do not revoke an existing open-file description.

This PR adds `test_g3_seccomp_scm_rights_cut.py` and a dedicated GitHub CI contrast job:

1. Use the same disposable `g3_monitor.Store` and real filesystem output; publish one bounded HTML marker and acknowledge HOLD. Any new broker write is refused.
2. A privileged test parent deliberately opens an append-writable FD for the existing output, simulating the bypass-capable condition in #475.
3. Spawn a separate UID 65534 child using a **trusted pre-exec launcher**; allow only standard input/output/error and the designated unprivileged Unix IPC socket FD through `subprocess.Popen(close_fds=True, pass_fds=...)`. No writable artifact FD is inherited.
4. Before `exec`, install `PR_SET_NO_NEW_PRIVS` and a real kernel seccomp classic-BPF filter. Reject unexpected architecture and the x32 syscall ABI; deny `recvmsg`, `recvmmsg`, `pidfd_getfd`, descriptor duplication, and `io_uring` setup/operations with `EPERM`.
5. After the child announces it is running under `Seccomp: 2`, the parent attempts to send its previously opened writable artifact FD via `sendmsg(SCM_RIGHTS)`.
6. Child `recvmsg` is denied with `EPERM`, path-based access is denied, no unexpected FD is inherited, and the protected artifact bytes and integrity inventory remain unchanged.

The dedicated workflow tests **both sides**: historical unrestricted child **does** write after HOLD (#475, expected negative control); confined child **does not** acquire the descriptor or write to the artifact (new test).

### Local replay (requires disposable root-capable Linux x86-64 test host)

```sh
cd evidence/execution-boundary/g3_prod_01
sudo -n python3 -B -m unittest -v \
  test_g3_scm_rights_cut.py test_g3_seccomp_scm_rights_cut.py
```

Use the exact PR-head GitHub workflow logs as evidence. No secrets, network service or persistent host modifications are required; tests use an isolated temporary directory and terminate the child.

## What this DOES prove under tested conditions

The configured kernel rejects `recvmsg` in a child with its filter installed **before untrusted program execution**, so the attempted post-HOLD `SCM_RIGHTS` delivery does not become a usable child write capability in that single path. Child path reopening is separately denied by DAC. Protected output stays unchanged in this test.

## What this does NOT prove

- A privileged delegator/root can already write to the same file itself. This experiment **does not constrain all privileged actors** or revoke all existing writable capabilities.
- This is a **deny-list demonstration**, not a production syscall allow-list, a complete LSM/MAC confinement policy, or confinement for other architectures/kernels.
- The intentionally inherited IPC socket is only safe in this experiment because it is a bounded local test and the kernel blocks its descriptor-receiving syscalls. Arbitrary application sockets, inherited aliases, shared mappings, mount namespaces and other write channels remain untested.
- This does not integrate the actual PR #507 veto-bound signed service; the test uses the historical bare `Store` solely to reproduce #475's exact failure mode. **The production candidate must combine a single veto-bound writer with confined process identities and an independently enumerated entire effect surface.**
- Neither full original-six X3 coverage, authentic consent, actual-world source correspondence, nor universal physical G3 is established.

## Next engineering integration

An explicit, independently provisioned service must ensure untrusted clients do not start with protected-output capabilities, cannot gain them through any permitted IPC, and have no alternate direct or indirect effect path. Production-grade enforcement should prefer a minimal **allow-listed** seccomp profile together with kernel DAC, namespaces and LSM policy, rather than treating this deny-list as sufficient. The trusted writer should close its writable staging FD before publication, avoid delegating any write-capable handle, and run as a dedicated non-root UID. Independently replay `SCM_RIGHTS`, inheritance, `pidfd_getfd`, aliases/hardlinks, shared memory, filesystem mounts and privileged write attempts.

Retain #475 as the load-bearing unsafe control. Retain [draft PR #507](https://github.com/Tobillicious/universal-protection-theory/pull/507) as the separately reviewed withdrawal/publication ordering repair. Neither one by itself certifies the combined service.
