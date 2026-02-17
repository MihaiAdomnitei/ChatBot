
## Run
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000

## API
- POST /chats → create new patient
- POST /chats/{id}/message → send doctor message
- GET  /chats/{id} → retrieve conversation

## Notes
- Model loads once
- Each chat is stateful
- Diagnosis never revealed
