"""Proof evidence extractor.

Reads Lean source files and produces a machine-readable summary of
the proof state: theorem count, sorry count, module list, key results.

No build system required — reads .lean files directly.
"""
import os
import re
from pathlib import Path

LEAN_DIR = "evidence/physical-bridges/PhysicalBridges"

KEY_RESULTS = [
    ("G1: Something IS", "SOMETHING_IS", "AbsoluteEnder P → False"),
    ("G2: G is unique fixed point", "G_FROM_NOTHING", "AbsoluteEnder (S → S) → False"),
    ("G3: Conditional universal protection", "if_bcrd_then_all_six_and_no_E", "BCRDIsQG → all six X3 + no E"),
    ("B7: State-determined causal accessibility", "state_determines_causal_accessibility", "Same dynamics, different sectors, different pathways"),
    ("B7: Sector structure", "sector_structure_of_CLM", "Relational gating is an operator property"),
    ("Koru: Spiral never returns", "THE_SPIRAL_NEVER_RETURNS", "No configuration recurs"),
    ("Koru: Nothing is lost", "NOTHING_IS_LOST_ON_THE_SPIRAL", "Every earlier history is a suffix of every later"),
    ("Genesis: In the beginning", "IN_THE_BEGINNING", "The first witness already refutes E"),
]


def scan_lean_files(repo_root):
    lean_dir = Path(repo_root) / LEAN_DIR
    if not lean_dir.exists():
        return []

    modules = []
    for lean_file in sorted(lean_dir.glob("*.lean")):
        text = lean_file.read_text(errors="replace")
        theorems = len(re.findall(r"^theorem\s", text, re.MULTILINE))
        defs = len(re.findall(r"^def\s", text, re.MULTILINE))
        sorry_count = len(re.findall(r"\bsorry\b", text))
        sorry_ax = len(re.findall(r"\bsorryAx\b", text))

        if theorems > 0 or defs > 0:
            modules.append({
                "name": lean_file.stem,
                "theorems": theorems,
                "definitions": defs,
                "sorry": sorry_count,
                "sorryAx_in_axiom_report": sorry_ax,
            })

    return modules


def find_key_results(repo_root):
    lean_dir = Path(repo_root) / LEAN_DIR
    found = []

    all_text = ""
    for lean_file in lean_dir.glob("*.lean"):
        all_text += lean_file.read_text(errors="replace") + "\n"

    for label, ident, description in KEY_RESULTS:
        present = ident in all_text
        found.append({
            "label": label,
            "identifier": ident,
            "description": description,
            "present": present,
        })

    return found


def full_evidence(repo_root):
    modules = scan_lean_files(repo_root)
    key = find_key_results(repo_root)

    total_theorems = sum(m["theorems"] for m in modules)
    total_sorry = sum(m["sorry"] for m in modules)
    total_sorry_ax = sum(m["sorryAx_in_axiom_report"] for m in modules)

    return {
        "schema": "gmesh-proof-evidence-v1",
        "total_theorems": total_theorems,
        "total_definitions": sum(m["definitions"] for m in modules),
        "total_sorry": total_sorry,
        "total_sorryAx_in_reports": total_sorry_ax,
        "module_count": len(modules),
        "key_results": key,
        "key_results_found": sum(1 for k in key if k["present"]),
        "modules": modules,
        "scope": "source file scan only — not a build or type-check",
    }
