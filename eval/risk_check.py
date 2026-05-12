"""
Check risk levels by hand.

Asks you about 10 clauses one at a time. Type L, M, or H for each one.
At the end it shows how often the system agreed with you.

run: python risk_check.py
"""

import json
import os
import random
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "backend"))

from dotenv import load_dotenv
load_dotenv(ROOT / "backend" / ".env")

import openai
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    print("ERROR: OPENAI_API_KEY not set in backend/.env")
    sys.exit(1)

from gpt_api_calls import classify_clause, assess_risk
from huggingface_hub import hf_hub_download
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


def get_clauses():
    print("Downloading CUAD dataset...")
    path = hf_hub_download(
        repo_id="theatticusproject/cuad",
        filename="CUAD_v1/CUAD_v1.json",
        repo_type="dataset",
    )
    with open(path) as f:
        data = json.load(f)

    label_re = re.compile(r'"([^"]+)"')
    clauses = []
    seen = set()

    for entry in data["data"]:
        for para in entry["paragraphs"]:
            for qa in para["qas"]:
                m = label_re.search(qa["question"])
                if not m:
                    continue
                cuad_label = m.group(1)
                for ans in qa.get("answers", []):
                    text = ans["text"].strip()
                    if len(text) < 35 or len(text) > 600:
                        continue
                    if text in seen:
                        continue
                    seen.add(text)
                    clauses.append(text)

    return clauses


def ask_for_label(idx, total, clause):
    print()
    print("-" * 60)
    print(f"Clause {idx}/{total}:")
    print()
    print(clause)
    print()
    while True:
        ans = input("Your risk? (L = Low, M = Medium, H = High): ").strip().lower()
        if ans in ("l", "low"):
            return "Low"
        if ans in ("m", "medium"):
            return "Medium"
        if ans in ("h", "high"):
            return "High"
        print("Please type L, M, or H.")


def main():
    num_to_label = 10

    clauses = get_clauses()
    rng = random.Random(42)
    rng.shuffle(clauses)
    picks = clauses[:num_to_label]

    human = []
    system = []

    print()
    print(f"You will label {num_to_label} clauses. Type L, M, or H for each.")
    print("Press Ctrl+C to quit early.")

    for i, text in enumerate(picks, 1):
        # ask the system first so its prediction is ready
        category = (classify_clause(text) or "").strip()
        sys_risk = (assess_risk(text, category) or "").strip().capitalize()

        # then ask the user (without showing them the system's answer)
        my_risk = ask_for_label(i, num_to_label, text)

        human.append(my_risk)
        if sys_risk in ("Low", "Medium", "High"):
            system.append(sys_risk)
        else:
            system.append("Low")  # fallback if system gave us junk

    # results
    acc = accuracy_score(human, system)
    p, r, f1, _ = precision_recall_fscore_support(
        human, system, average="macro",
        labels=["Low", "Medium", "High"], zero_division=0,
    )

    print()
    print("=" * 60)
    print(f"  Risk evaluation  (n = {len(human)})")
    print("=" * 60)
    print(f"  Accuracy:           {acc:.3f}")
    print(f"  Precision (macro):  {p:.3f}")
    print(f"  Recall    (macro):  {r:.3f}")
    print(f"  F1        (macro):  {f1:.3f}")
    print()
    print(f"  My labels:      {dict(Counter(human))}")
    print(f"  System labels:  {dict(Counter(system))}")

    levels = ["Low", "Medium", "High"]
    print()
    print("  Confusion matrix (rows = me, cols = system):")
    print("              " + "  ".join(f"{l:>8}" for l in levels))
    for tl in levels:
        cells = []
        for pl in levels:
            count = 0
            for h, s in zip(human, system):
                if h == tl and s == pl:
                    count += 1
            cells.append(count)
        print(f"  {tl:>8}    " + "  ".join(f"{c:>8}" for c in cells))


if __name__ == "__main__":
    main()
