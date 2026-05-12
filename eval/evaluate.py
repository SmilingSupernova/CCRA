"""
Compare our system to CUAD and a keyword baseline.

run: python evaluate.py
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

from gpt_api_calls import classify_clause
from huggingface_hub import hf_hub_download
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


BACKEND_CATEGORIES = [
    "Document Name", "Agreement Date", "Parties", "Governing Law", "Effective Date",
    "Expiration Date", "Renewal Term", "Notice Period to Terminate Renewal",
    "Termination for Convenience", "Exclusivity", "Non-Compete", "No-Solicit of Customers",
    "No-Solicit of Employees", "Competitive Restriction Exception", "Covenant not to Sue",
    "Most Favored Nation/MFN", "Non-Disparagement", "Minimum Commitment",
    "Volume Restriction", "License Grant", "Irrevocable or Perpetual License",
    "Affiliate License-Licensor", "Affiliate License-Licensee",
    "Unlimited/All-You-Can-Eat-License", "Source Code Escrow", "IP Ownership Assignment",
    "Joint IP Ownership", "Cap on Liability", "Uncapped Liability", "Liquidated Damages",
    "Revenue/Profit Sharing", "Insurance", "Anti-Assignment", "Non-Transferable License",
    "Change of Control", "Audit Rights", "Post-Termination Services", "ROFR/ROFN/ROFO",
    "Third Party Beneficiary", "Warranty Duration",
]

CUAD_TO_BACKEND = {
    "Document Name": "Document Name", "Parties": "Parties", "Agreement Date": "Agreement Date",
    "Effective Date": "Effective Date", "Expiration Date": "Expiration Date",
    "Renewal Term": "Renewal Term",
    "Notice Period To Terminate Renewal": "Notice Period to Terminate Renewal",
    "Governing Law": "Governing Law", "Most Favored Nation": "Most Favored Nation/MFN",
    "Non-Compete": "Non-Compete", "Exclusivity": "Exclusivity",
    "No-Solicit Of Customers": "No-Solicit of Customers",
    "Competitive Restriction Exception": "Competitive Restriction Exception",
    "No-Solicit Of Employees": "No-Solicit of Employees",
    "Non-Disparagement": "Non-Disparagement",
    "Termination For Convenience": "Termination for Convenience",
    "Rofr/Rofo/Rofn": "ROFR/ROFN/ROFO", "Change Of Control": "Change of Control",
    "Anti-Assignment": "Anti-Assignment", "Revenue/Profit Sharing": "Revenue/Profit Sharing",
    "Minimum Commitment": "Minimum Commitment", "Volume Restriction": "Volume Restriction",
    "Ip Ownership Assignment": "IP Ownership Assignment",
    "Joint Ip Ownership": "Joint IP Ownership", "License Grant": "License Grant",
    "Non-Transferable License": "Non-Transferable License",
    "Affiliate License-Licensor": "Affiliate License-Licensor",
    "Affiliate License-Licensee": "Affiliate License-Licensee",
    "Unlimited/All-You-Can-Eat-License": "Unlimited/All-You-Can-Eat-License",
    "Irrevocable Or Perpetual License": "Irrevocable or Perpetual License",
    "Source Code Escrow": "Source Code Escrow",
    "Post-Termination Services": "Post-Termination Services", "Audit Rights": "Audit Rights",
    "Uncapped Liability": "Uncapped Liability", "Cap On Liability": "Cap on Liability",
    "Liquidated Damages": "Liquidated Damages", "Warranty Duration": "Warranty Duration",
    "Insurance": "Insurance", "Covenant Not To Sue": "Covenant not to Sue",
    "Third Party Beneficiary": "Third Party Beneficiary",
}

KEYWORDS = {
    "Document Name": ["agreement", "this contract"],
    "Agreement Date": ["dated as of", "entered into on"],
    "Parties": ["between", "by and between"],
    "Governing Law": ["governed by", "laws of the state"],
    "Effective Date": ["effective date", "shall become effective"],
    "Expiration Date": ["expire", "expiration"],
    "Renewal Term": ["renewal", "automatically renew"],
    "Notice Period to Terminate Renewal": ["prior written notice", "days prior to"],
    "Termination for Convenience": ["terminate", "without cause", "for convenience"],
    "Exclusivity": ["exclusive", "exclusively"],
    "Non-Compete": ["shall not compete", "non-compete"],
    "No-Solicit of Customers": ["solicit", "customers"],
    "No-Solicit of Employees": ["solicit", "employees"],
    "Competitive Restriction Exception": ["exception", "shall not apply"],
    "Covenant not to Sue": ["covenant not to sue", "will not sue"],
    "Most Favored Nation/MFN": ["most favored"],
    "Non-Disparagement": ["disparage"],
    "Minimum Commitment": ["minimum", "at least"],
    "Volume Restriction": ["volume", "not exceed"],
    "License Grant": ["grants", "license"],
    "Irrevocable or Perpetual License": ["irrevocable", "perpetual"],
    "Affiliate License-Licensor": ["affiliate", "licensor"],
    "Affiliate License-Licensee": ["affiliate", "licensee"],
    "Unlimited/All-You-Can-Eat-License": ["unlimited"],
    "Source Code Escrow": ["source code", "escrow"],
    "IP Ownership Assignment": ["intellectual property", "ownership"],
    "Joint IP Ownership": ["joint", "jointly own"],
    "Cap on Liability": ["shall not exceed", "cap"],
    "Uncapped Liability": ["unlimited liability"],
    "Liquidated Damages": ["liquidated damages"],
    "Revenue/Profit Sharing": ["revenue", "profit"],
    "Insurance": ["insurance", "insure"],
    "Anti-Assignment": ["shall not assign"],
    "Non-Transferable License": ["non-transferable"],
    "Change of Control": ["change of control", "merger"],
    "Audit Rights": ["audit", "inspect"],
    "Post-Termination Services": ["post-termination"],
    "ROFR/ROFN/ROFO": ["right of first refusal"],
    "Third Party Beneficiary": ["third party beneficiary"],
    "Warranty Duration": ["warranty", "warrants"],
}


def load_cuad_clauses():
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
                if cuad_label not in CUAD_TO_BACKEND:
                    continue
                category = CUAD_TO_BACKEND[cuad_label]

                for ans in qa.get("answers", []):
                    text = ans["text"].strip()
                    if len(text) < 35:
                        continue
                    if (text, category) in seen:
                        continue
                    seen.add((text, category))
                    clauses.append((text, category))

    print(f"Loaded {len(clauses)} labeled clauses from CUAD")
    return clauses


def sample_balanced(clauses, per_category=5, seed=42):
    rng = random.Random(seed)
    by_cat = {}
    for text, cat in clauses:
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append((text, cat))

    sample = []
    for cat in by_cat:
        rng.shuffle(by_cat[cat])
        sample.extend(by_cat[cat][:per_category])

    rng.shuffle(sample)
    print(f"Sampled {len(sample)} clauses ({per_category} per category)")
    return sample


def normalize_category(raw):
    if not raw:
        return None
    raw = raw.strip()
    if raw in BACKEND_CATEGORIES:
        return raw
    for c in BACKEND_CATEGORIES:
        if c.lower() == raw.lower():
            return c
    return None


def llm_predict_all(clauses):
    preds = []
    print(f"Running LLM on {len(clauses)} clauses...")

    for i, (text, true_cat) in enumerate(clauses, 1):
        raw = classify_clause(text) or ""
        pred = normalize_category(raw)
        if pred is None:
            pred = "Governing Law"
        preds.append(pred)
        if i % 20 == 0:
            print(f"  [{i}/{len(clauses)}]")

    return preds


def keyword_predict(text):
    text_lower = text.lower()
    best_cat = "Governing Law"
    best_score = 0

    for cat in KEYWORDS:
        score = 0
        for kw in KEYWORDS[cat]:
            if kw in text_lower:
                score += 1
        if score > best_score:
            best_score = score
            best_cat = cat

    return best_cat


def keyword_predict_all(clauses):
    out = []
    for text, _ in clauses:
        out.append(keyword_predict(text))
    return out


def print_metrics(name, y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    p_w, r_w, f1_w, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    print()
    print("=" * 60)
    print(f"  {name}")
    print("=" * 60)
    print(f"  Accuracy:              {acc:.3f}")
    print(f"  Precision (macro):     {p_macro:.3f}")
    print(f"  Recall    (macro):     {r_macro:.3f}")
    print(f"  F1        (macro):     {f1_macro:.3f}")
    print(f"  Precision (weighted):  {p_w:.3f}")
    print(f"  Recall    (weighted):  {r_w:.3f}")
    print(f"  F1        (weighted):  {f1_w:.3f}")


def print_top_confusions(y_true, y_pred, n=10):
    mistakes = Counter()
    for t, p in zip(y_true, y_pred):
        if t != p:
            mistakes[(t, p)] += 1
    if not mistakes:
        return
    print(f"\n  Top {n} confusions (true -> predicted, count):")
    for (t, p), c in mistakes.most_common(n):
        print(f"    {t}  ->  {p}  ({c})")


def consistency_check(clauses, n=10):
    print()
    print("=" * 60)
    print("  Consistency check (same clause, run twice)")
    print("=" * 60)

    rng = random.Random(123)
    picks = rng.sample(clauses, min(n, len(clauses)))

    same = 0
    for text, _ in picks:
        a = normalize_category(classify_clause(text) or "")
        b = normalize_category(classify_clause(text) or "")
        if a == b:
            same += 1

    pct = same / len(picks)
    print(f"  Same category both runs: {same}/{len(picks)}  ({pct:.0%})")


def main():
    clauses = load_cuad_clauses()
    sample = sample_balanced(clauses, per_category=5)

    y_true = []
    for _, cat in sample:
        y_true.append(cat)

    y_pred_llm = llm_predict_all(sample)
    y_pred_kw = keyword_predict_all(sample)

    print_metrics("LLM system (GPT-4o-mini)", y_true, y_pred_llm)
    print_top_confusions(y_true, y_pred_llm)

    print_metrics("Keyword baseline", y_true, y_pred_kw)

    consistency_check(sample, n=10)

    print()
    print("Done. For risk levels run: python risk_check.py")


if __name__ == "__main__":
    main()
