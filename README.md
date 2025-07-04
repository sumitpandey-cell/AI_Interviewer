# InterviewAI - AI-Powered Technical Interview Practice

InterviewAI is a comprehensive interview practice platform that uses AI to simulate technical interviews across various domains. The application provides realistic interview experiences, real-time feedback, and detailed analysis of your performance.

## Features

- **AI-Powered Interviews**: Practice technical interviews with an AI interviewer that adapts to your responses.
- **Voice Interaction**: Natural voice-based conversations with the AI interviewer.
- **Real-time Feedback**: Get immediate feedback on your interview performance.
- **Detailed Analysis**: Comprehensive post-interview analysis of your technical knowledge, communication skills, and problem-solving abilities.
- **Interview History**: Track your progress and review past interview sessions.

## Architecture

The application consists of two main components:

### Frontend (React + TypeScript)

- Built with React and TypeScript
- Uses Vite for fast development and optimized production builds
- UI components from Shadcn UI library
- Voice recording and playback features for interactive interviews

### Backend (Python + Flask)

- Flask API server for handling interview sessions
- Integration with AI language models for interview simulation
- Speech-to-text and text-to-speech capabilities

## Interview Session Tracking & Storage

The application implements robust interview session tracking and storage using Supabase as the backend database.

### Data Structure

1. **Interviews Table**
   - Stores metadata about each interview session
   - Fields: user_id, session_id, topic, start_time, end_time, duration_seconds, question_count, conversation_state, etc.

2. **Conversation Messages Table**
   - Stores individual messages exchanged during an interview
   - Fields: interview_id, speaker (AI or User), text, timestamp, sequence

3. **Feedback Table**
   - Stores AI-generated feedback and analysis of each interview
   - Fields: interview_id, overall_score, skills_assessment, strengths, areas_for_improvement, etc.

### Implementation Details

1. **Interview Progress Tracking**
   - The application tracks both question count and AI speaking state to ensure accurate interview progress monitoring.
   - The redirect to the feedback page only occurs after the AI has finished speaking the last response.

2. **Data Storage Flow**
   - When an interview is completed, all conversation data is saved to Supabase.
   - The interview ID is stored in the application state and used for feedback association.
   - Feedback is saved both automatically upon generation and via a manual save button.

3. **User Dashboard**
   - Displays interview history and performance metrics from Supabase.
   - Shows average scores, total practice time, and interview counts.

## Database Setup

The database schema is defined in `supabase_setup.sql` and includes:
- Tables for interviews, conversation_messages, and feedback
- Row-level security policies to ensure data privacy
- Indexes for optimized query performance

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- Supabase account

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/interviewai.git
   cd interviewai
   ```

2. Set up the frontend:
   ```
   cd frontend
   npm install
   ```

3. Set up the backend:
   ```
   cd ../backend
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in the frontend directory with your Supabase credentials:
     ```
     VITE_SUPABASE_PROJECT_URL=your_supabase_url
     VITE_SUPABASE_KEY=your_supabase_anon_key
     ```

### Running the Application

1. Start the backend server:
   ```
   cd backend
   python app.py
   ```

2. Start the frontend development server:
   ```
   cd frontend
   npm run dev
   ```

3. Access the application at `http://localhost:5173`