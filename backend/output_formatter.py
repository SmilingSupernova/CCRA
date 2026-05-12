"""
Formats the results from the GPT API calls and enitities and phrases
into a structured output that gets returned to the frontend.
"""

import json


# bundles all the info we have for a single clause into one dictionary
def format_clause(clause_number, text, category, risk, explanation, entities, keyphrases):
    clause = {}

    clause["clause_number"] = clause_number
    clause["text"] = text
    clause["category"] = category
    clause["risk"] = risk
    clause["explanation"] = explanation
    clause["entities"] = entities
    clause["keyphrases"] = keyphrases

    return clause


# collects all individual clause dictionaries into one list
def format_all_clauses(clauses):
    output = []

    for clause in clauses:
        output.append(clause)

    return output


# bundles the contract-level summary together with the list of clauses
def format_final_output(summary, clauses):
    return {
        "summary": summary,
        "clauses": clauses,
    }


# converts the final output into a JSON string to send to the frontend
def to_json(formatted_output):
    return json.dumps(formatted_output, indent=4)
