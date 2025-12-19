venv\Scripts\activate
cd frontend
npm start
cd backend      
python -m uvicorn app.main:app --reload