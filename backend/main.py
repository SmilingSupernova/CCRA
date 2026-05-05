"""
This is the main file that runs the FastAPI server and ties everything together.

The pipeline for each clause goes like this:
    1. Preprocessor splits the raw contract into individual clauses
    2. GPT classifies the clause into a CUAD category (API call 1)
    3. GPT assesses the risk level based on the clause wording (API call 2)
    4. GPT generates a plain-English explanation of the clause (API call 3)
    5. spaCy extracts named entities from the clause (runs locally, no API call)
    6. YAKE extracts the most important legal keyphrases (runs locally, no API call)
    7. Everything gets bundled into a JSON object and returned to the frontend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from preprocessor import get_clauses
from gpt_api_calls import classify_clause, assess_risk, explain_clause
from output_formatter import format_clause, format_all_clauses
from entities_and_phrases import extract_entities, extract_keyphrases
from file_reader import extract_text

# load the OpenAI API key from the .env file
load_dotenv()

app = FastAPI()

# allow the frontend to talk to this backend regardless of what port it runs on
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# this defines what the request body should look like when the frontend sends a contract
class ContractRequest(BaseModel):
    contract_text: str


# simple health check so you can confirm the server is running
@app.get("/")
def health_check():
    return {"status": "server is running"}


def run_analysis(contract_text):
    # reject empty input right away before doing anything else
    if not contract_text.strip():
        raise HTTPException(status_code=400, detail="Contract text cannot be empty.")

    # breaking the contract into individual clauses using the preprocessor
    print("Splitting contract into clauses...")
    clauses = get_clauses(contract_text)

    # if nothing came back from the preprocessor, return an empty list instead of crashing
    if not clauses:
        print("No clauses found in the contract.")
        return []

    print(f"Found {len(clauses)} clauses. Starting analysis...")

    # this will hold the formatted result for each clause
    all_formatted_clauses = []

    for clause_number, clause_text in enumerate(clauses, start=1):

        print(f"Analyzing clause {clause_number} of {len(clauses)}...")

        # classify the clause into a CUAD category (API call 1)
        category = classify_clause(clause_text)

        # if classification failed for some reason, skip this clause and move on
        if category is None:
            print(f"Clause {clause_number}: classification failed, skipping.")
            continue

        # asking GPT to assess the risk based on the actual wording of the clause (API call 2)
        risk = assess_risk(clause_text, category)

        if risk is None:
            print(f"Clause {clause_number}: risk assessment failed, using fallback.")
            risk = "Unknown"

        # asking GPT to explain why this clause matters or could be risky (API call 3)
        explanation = explain_clause(clause_text, category, risk)

        # if explanation failed, fall back to a safe default
        if explanation is None:
            print(f"Clause {clause_number}: explanation failed, using fallback.")
            explanation = "No explanation available."

        # extract named entities from the clause using spaCy
        entities = extract_entities(clause_text)

        # extract the most legally significant keyphrases using YAKE
        keyphrases = extract_keyphrases(clause_text)

        # bundle everything for this clause into one dictionary
        formatted = format_clause(
            clause_number=clause_number,
            text=clause_text,
            category=category,
            risk=risk,
            explanation=explanation,
            entities=entities,
            keyphrases=keyphrases
        )

        all_formatted_clauses.append(formatted)

    print("Analysis complete. Returning results.")
    return format_all_clauses(all_formatted_clauses)


@app.post("/analyze")
def analyze_contract(body: ContractRequest):
    return run_analysis(body.contract_text)


@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        contract_text = extract_text(file.filename or "", file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("Error extracting text from file:", e)
        raise HTTPException(status_code=400, detail="Could not read the uploaded file.")

    return run_analysis(contract_text)
