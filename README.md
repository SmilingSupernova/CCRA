# Contract Clause Classification and Risk Analysis

Our app analyzes legal contracts and breaks them down clause by clause. It accepts pasted text or .txt, .pdf, and .docx uploads, then splits the contract into clauses and classifies each one into a CUAD category. Every clause is assigned a risk level, given a short explanation, and tagged with extracted entities and keyphrases. The app also generates an overall summary of the contract.

## How it works

The backend splits the contract into clauses and runs three GPT-4o-mini calls per clause to produce the category, risk level, and explanation. Named entities are extracted locally with spaCy and keyphrases with YAKE. A final GPT API call generates a short summary of the entire contract. 

## Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- An OpenAI API key

## Backend

Install dependencies:
cd backend
pip install -r requirements.txt

Configure environment:
cp .env.example .env                
then edit .env and set OPENAI_API_KEY


Run:
uvicorn main:app --reload
Backend runs on http://localhost:8000.

## Frontend

Install dependencies:
cd frontend
npm install


Run:
npm run dev

Frontend runs on http://localhost:5173.

Start the backend first, then the frontend.

## Using the demo

Open http://localhost:5173 in the browser. Paste contract text into the textbox or upload a .txt, .pdf, or .docx file to populate it. Click "Analyze contract" to run the pipeline and see the results.

