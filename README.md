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
