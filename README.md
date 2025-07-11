# AI Interviewer

AI Interviewer is a complete interview practice platform with an AI-powered interviewer that provides real-time feedback and analysis.

## Project Structure

This project consists of two main components:

1. **Backend (`ai_interviewer/`)**: A FastAPI server providing the AI interview functionality
2. **Frontend (`lucid-interview-agent-main/`)**: A React web application providing the user interface

## Prerequisites

- Python 3.10+ for the backend
- Node.js 18+ for the frontend
- tmux (for the development script)

## Getting Started

### Setting Up the Backend

1. Navigate to the backend directory:
   ```bash
   cd ai_interviewer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   alembic upgrade head
   ```

### Setting Up the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd lucid-interview-agent-main
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Running Both Services

You can run both the backend and frontend with our development script:

```bash
./start-dev.sh
```

This will start:
- Backend at http://localhost:8000
- Frontend at http://localhost:5173

### Starting Services Separately

**Backend:**
```bash
cd ai_interviewer
python -m src.ai_interviewer.main
```

**Frontend:**
```bash
cd lucid-interview-agent-main
npm run dev
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login a user

### Interviews
- `POST /interviews/` - Create a new interview
- `GET /interviews/` - Get all interviews for the current user
- `GET /interviews/{interview_id}` - Get a specific interview
- `POST /interviews/{interview_id}/start` - Start an interview
- `POST /interviews/session/submit` - Submit a response to the current question

### WebSockets
- `WebSocket /ws/interview/{session_token}` - Real-time interview communication

## Technologies Used

### Backend
- FastAPI - Web framework
- SQLAlchemy - ORM
- Alembic - Database migrations
- LangGraph - AI workflow
- WebSockets - Real-time communication

### Frontend
- React - UI library
- Vite - Build tool
- TailwindCSS - Styling
- shadcn/ui - Component library
- React Query - Data fetching
- React Router - Routing