# Contract Clause Classification and Risk Analysis

This app analyzes legal contracts and breaks them down clause by clause. It accepts pasted text or `.txt`, `.pdf`, and `.docx` uploads, then splits the contract into clauses and classifies each one into a CUAD category. Every clause is assigned a risk level, given a plain-English explanation, and tagged with extracted entities and keyphrases. The app also generates an overall summary of the contract.

## How it works

The backend splits the contract into clauses and runs three GPT-4o-mini calls per clause to produce the category, risk level, and explanation. Named entities are extracted locally with spaCy and keyphrases with YAKE, so those steps do not hit the API. A final GPT call generates the contract-level summary.

## Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- An OpenAI API key

## Backend

Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

Configure environment:
```bash
cp .env.example .env                # then edit .env and set OPENAI_API_KEY
```

Run:
```bash
uvicorn main:app --reload
```
Backend runs on `http://localhost:8000`.

## Frontend

Install dependencies:
```bash
cd frontend
npm install
```

Run:
```bash
npm run dev
```
Frontend runs on `http://localhost:5173`.

Start the backend first, then the frontend.

## Using the demo

Open `http://localhost:5173` in your browser. Paste contract text into the textbox or upload a `.txt`, `.pdf`, or `.docx` file to populate it. Click "Analyze contract" to run the pipeline and see the results.

## Project structure

```
backend/
  main.py                  — FastAPI app and pipeline
  preprocessor.py          — splits contract into clauses
  gpt_api_calls.py         — three GPT calls per clause plus summary
  entities_and_phrases.py  — spaCy NER and YAKE keyphrases
  file_reader.py           — handles .txt, .pdf, .docx uploads
  output_formatter.py      — builds the final JSON response
frontend/                  — React + Vite + Tailwind UI
```
