"""
Handles all 3 api calls to GPT-4o-mini for each clause in the contract
"""

import os
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")


# sends the clause to GPT and returns a CUAD category
def classify_clause(clause_text):
    system_message = """You are an expert legal analyst who reviews commercial contracts. Classify a single contract clause into one of the CUAD categories listed below.

Read the clause carefully and decide which category best describes what the clause is doing. Focus on the clause's primary purpose, not on incidental words it may contain.

Respond with ONLY the category name, exactly as written in this list, and nothing else:

Document Name, Agreement Date, Parties, Governing Law, Effective Date, Expiration Date, Renewal Term, Notice Period to Terminate Renewal, Termination for Convenience, Exclusivity, Non-Compete, No-Solicit of Customers, No-Solicit of Employees, Competitive Restriction Exception, Covenant not to Sue, Most Favored Nation/MFN, Non-Disparagement, Minimum Commitment, Volume Restriction, License Grant, Irrevocable or Perpetual License, Affiliate License-Licensor, Affiliate License-Licensee, Unlimited/All-You-Can-Eat-License, Source Code Escrow, IP Ownership Assignment, Joint IP Ownership, Cap on Liability, Uncapped Liability, Liquidated Damages, Revenue/Profit Sharing, Insurance, Anti-Assignment, Non-Transferable License, Change of Control, Audit Rights, Post-Termination Services, ROFR/ROFN/ROFO, Third Party Beneficiary, Warranty Duration

Here are some examples to guide you:

Example 1
Clause: This Agreement shall be governed by and construed in all respects in accordance with the laws of the State of New York, without giving effect to any conflicts of laws principles.
Category: Governing Law

Example 2
Clause: Subject to the terms set forth in this agreement, Erchonia grants Distributor the exclusive, non-transferable right and license to promote, distribute and sell the Products identified in Exhibit A to those type of customer specified in Exhibit B and only within the Territory specified in Exhibit B.
Category: License Grant

Example 3
Clause: Either party may terminate this Agreement, without cause, upon ninety (90) days prior written notice to the other party, provided, however, that all outstanding Work Orders shall continue to be governed by the terms and conditions hereof.
Category: Termination for Convenience

Example 4
Clause: Licensee shall not assign or otherwise transfer any of its rights, or delegate or otherwise transfer any of its obligations or performance, under this Agreement, in each case whether voluntarily, involuntarily, by operation of law or otherwise, without Licensor's prior written consent.
Category: Anti-Assignment

Example 5
Clause: EACH PARTY'S LIABILITY ARISING OUT OF OR RELATED TO THIS AGREEMENT WILL NOT EXCEED AN AMOUNT EQUAL TO THE AGGREGATE AMOUNTS PAID OR PAYABLE TO LICENSOR IN THE TWELVE (12) MONTHS PRECEDING THE COMMENCEMENT OF THE CLAIM.
Category: Cap on Liability

Example 6
Clause: During the Term, and for a period of twelve (12) months thereafter, Rogers (and its representatives) shall have the right, upon reasonable prior written notice to Licensor, and during regular business hours, to inspect and/or audit Licensor's books and records to confirm compliance with Licensor's obligations under this Section.
Category: Audit Rights

Now classify the clause provided by the user."""

    user_message = "Clause: " + clause_text

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2
        )

        category = response.choices[0].message.content.strip()
        return category

    except Exception as e:
        print("Error during classification: ", e)
        return None


# sends clause and category to GPT and returns a risk level
def assess_risk(clause_text, category):
    system_message = """You are an expert legal analyst who reviews commercial contracts. Assess the risk level of a single contract clause based on its actual wording.

Risk is assessed neutrally — not from one party's perspective, but based on how unusual, one-sided, or burdensome the clause is overall.

Use this rubric:
Low: standard market terms; mutual or balanced; nothing surprising.
Medium: somewhat aggressive or one-sided, but within the range of normal commercial contracts; worth noting but not a deal-breaker.
High: significantly one-sided, unusual, or creates substantial unbounded exposure; warrants pushback.

The category of the clause is given to you, but do not assume risk from the category alone. Two clauses in the same category can have very different risk levels depending on wording. Read the clause carefully.

Respond with EXACTLY ONE word from this list, nothing else: Low, Medium, High

Here are some examples to guide you:

Example 1
Category: Effective Date
Clause: This Agreement shall become effective upon the date first written above and shall remain in full force and effect for a period of two years (2), unless earlier terminated pursuant to the provisions in this Agreement.
Risk: Low

Example 2
Category: License Grant
Clause: Throughout the Term of this Agreement, the parties hereby agree to grant to each other a limited license to use each other's proprietary marks solely in connection with the sale, distribution, marketing and promotion of each party's calling cards by the other party.
Risk: Low

Example 3
Category: Renewal Term
Clause: This agreement shall automatically renew for additional successive terms of twelve (12) months each at the end of the Initial Term ("Renewal Terms"), unless either party notifies the other in writing at least sixty (60) days prior to the end of the Initial Term.
Risk: Medium

Example 4
Category: Cap on Liability
Clause: EACH PARTY'S LIABILITY ARISING OUT OF OR RELATED TO THIS AGREEMENT WILL NOT EXCEED AN AMOUNT EQUAL TO THE AGGREGATE AMOUNTS PAID OR PAYABLE TO LICENSOR IN THE TWELVE (12) MONTHS PRECEDING THE COMMENCEMENT OF THE CLAIM.
Risk: Medium

Example 5
Category: Insurance
Clause: Each Party, at its own expense, shall maintain comprehensive general liability, product liability and other appropriate insurance for the activities such Party undertakes pursuant to this Agreement, from reputable and financially secure insurance carriers in a form and at levels consistent with sound business practice and adequate in light of its obligations under this Agreement.
Risk: Medium

Example 6
Category: License Grant
Clause: ExxonMobil grants FCE a worldwide, non-exclusive, royalty-free, perpetual, irrevocable (except as stated in Paragraphs 12.03 (Failure to Perform), 12.04 (Other Termination), and 12.05 (Bankruptcy)), sub-licensable, non-transferable (except pursuant to Article 14 (Assignment)), right and license to practice Program Results solely for Power Applications and Hydrogen Applications.
Risk: High

Example 7
Category: Termination for Convenience
Clause: Theismann shall have the right to terminate this Agreement at any time upon thirty (30) days' written notice to Bizzingo, such termination to become effective at the conclusion of such 30-day period.
Risk: High

Example 8
Category: Non-Compete
Clause: Member covenants and agrees that during the Post-Term Period (defined below), except as otherwise approved in writing by Franchisor, Member shall not, either directly or indirectly, own, manage, engage in, be employed by, advise, make loans to, consult for, or have any other interest in any Competitive Business that is, or intends to operate, within a three (3) mile radius of the premises of your Franchised Business or within a three (3) mile radius of any Franchised Business then-operating or under construction to operate under the System.
Risk: High

Now assess the risk of the clause provided by the user."""

    user_message = "Category: " + category + "\nClause: " + clause_text

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2
        )

        risk = response.choices[0].message.content.strip()
        return risk

    except Exception as e:
        print("Error during risk assessment:", e)
        return None


# sends clause, category, and risk level to GPT and returns a short explanation
def explain_clause(clause_text, category, risk):
    system_message = """You are an expert legal analyst who explains contract clauses to non-lawyers. Your job is to write a short, plain-English explanation of a single clause.

Follow this structure exactly:
- Sentence 1: What the clause does in practical terms.
- Sentence 2: Which party it favors or burdens, and why it received the given risk level.

Keep the explanation between 45 and 60 words total.

Rules:
- Do not restate the category name (the user already sees it).
- Do not use the words "Low", "Medium", or "High", describe the level of concern in your own words instead.
- Vary your opening. Do not start every explanation with "This clause...".
- Avoid legal jargon where possible. Write the way you would explain it to somebody who is not a lawyer.
- Respond with only the explanation text. No headings, labels, or preambles."""

    user_message = "Category: " + category + "\nRisk Level: " + risk + "\nClause: " + clause_text

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        explanation = response.choices[0].message.content.strip()
        return explanation

    except Exception as e:
        print("Error during explanation:", e)
        return None
