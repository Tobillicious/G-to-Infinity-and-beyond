# G-Mesh — Join the Proof Network

Your computer becomes part of a network sharing mathematical proof that
protection is built into the structure of existence itself.

430+ theorems. Independently verifiable. No trust required.

---

## How to join (Mac)

### Step 1: Open Terminal

Press **Cmd + Space**, type **Terminal**, press **Enter**.

A window with a blinking cursor appears. This is where you paste the command.

### Step 2: Paste this and press Enter

```
curl -sSL https://raw.githubusercontent.com/Tobillicious/universal-protection-theory/main/gmesh/join.sh | bash
```

That's it. Your computer is now a node.

Every device on your wifi (phones, laptops, tablets) can see the proof
evidence by opening the link that appears in the window.

### Step 3: To stop

Press **Ctrl + C** in the Terminal window.

Nothing was installed. Nothing was changed on your computer.

---

## How to join (Windows)

### Step 1: Open PowerShell

Press the **Windows key**, type **PowerShell**, press **Enter**.

### Step 2: Paste this and press Enter

```
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/Tobillicious/universal-protection-theory/main/gmesh/join.py').read())"
```

If that doesn't work, you may need to install Python first:
go to [python.org/downloads](https://www.python.org/downloads/) and
click the big yellow Download button. Install it, then try again.

### Step 3: To stop

Press **Ctrl + C**.

---

## What does this do?

It runs a small program (about 300 lines — you can read every line
[here](https://github.com/Tobillicious/universal-protection-theory/blob/main/gmesh/join.py) — just open that link).

Your computer shares proof evidence with other devices on your network.
It does NOT install anything, does NOT change any files, does NOT collect
any data, and stops the moment you close the window.

## What is this proof?

Universal Protection Theory (UPT) is a mathematical proof that:

1. **Something exists** (proved — no assumptions needed)
2. **Good composes and grows** (proved — no assumptions needed)
3. **Protection of every person is a necessary consequence of existence**

The proofs are written in Lean 4, a language where a computer checks
every logical step. If it compiles, the logic holds. No trust needed.

Full proof: https://github.com/Tobillicious/universal-protection-theory

Start here: https://github.com/Tobillicious/universal-protection-theory/blob/main/THE-LAW-START-HERE.md

---

## Questions

**Is this safe?**
Yes. Read the code yourself — it's 300 lines of standard Python,
no network calls except fetching public theorem counts from GitHub.
Nothing is installed or saved.

**Do I need to understand maths?**
No. Your computer shares the evidence. The proofs are independently
verifiable by anyone who wants to check them.

**What if I close the window?**
It stops. That's it. Open Terminal and paste the command again any time.

**Can I verify the proofs myself?**
Yes. Install Lean 4 (https://leanprover.github.io/lean4/doc/setup.html),
clone the repository, and run `lake build`. The computer checks every
theorem from scratch. If it finishes without error, every proof holds.
