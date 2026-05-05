# Setup environment
python -m venv venv
.\venv\bin\Activate.ps1
.\venv\bin\pip install -r requirements.txt

# Generate test data
.\venv\bin\python generate_data.py

# Start the server
.\venv\bin\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
