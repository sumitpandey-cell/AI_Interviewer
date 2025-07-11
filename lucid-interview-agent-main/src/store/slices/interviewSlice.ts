import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { InterviewsAPI } from '@/lib/api';

// Define types
interface Interview {
  id: number;
  title: string;
  position: string;
  company_name?: string;
  description?: string;
  interview_type: string;
  status: string;
  created_at: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
  duration_minutes?: number;
}

interface InterviewSession {
  session_token: string;
  first_question: any;
  audio_data: any; // Audio from Google Cloud TTS
  workflow_state: any;
  is_resumed: boolean;
}

interface SubmitResponse {
  next_question: any;
  audio_data: any;
  is_completed: boolean;
  feedback?: any;
}

interface InterviewState {
  interviews: Interview[];
  currentInterview: Interview | null;
  interviewSession: InterviewSession | null;
  currentQuestion: string;
  currentResponse: SubmitResponse | null;
  loading: boolean;
  error: string | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
}

// Initial state
const initialState: InterviewState = {
  interviews: [],
  currentInterview: null,
  interviewSession: null,
  currentQuestion: '',
  currentResponse: null,
  loading: false,
  error: null,
  status: 'idle'
};

// Async thunks
export const fetchUserInterviews = createAsyncThunk(
  'interview/fetchUserInterviews',
  async (_, { rejectWithValue }) => {
    try {
      console.log("[REDUX DEBUG] Fetching user interviews...");
      const interviews = await InterviewsAPI.getUserInterviews();
      console.log("[REDUX DEBUG] Fetched interviews from API:", interviews);
      
      // Add validation to ensure we have an array
      if (!interviews || !Array.isArray(interviews)) {
        console.error("[REDUX DEBUG] API returned non-array interviews:", interviews);
        
        // Return empty array if API returns invalid data
        return [];
      }
      
      // Log each interview for debugging
      interviews.forEach((interview, index) => {
        console.log(`[REDUX DEBUG] Interview ${index}:`, {
          id: interview.id,
          title: interview.title,
          status: interview.status
        });
      });
      
      return interviews;
    } catch (error: any) {
      console.error("[REDUX DEBUG] Error fetching interviews:", error);
      return rejectWithValue(error.message || 'Failed to fetch interviews');
    }
  }
);

export const fetchInterview = createAsyncThunk(
  'interview/fetchInterview',
  async (id: number, { rejectWithValue, getState }) => {
    // Check if we already have this interview in the state
    const state = getState() as { interview: InterviewState };
    const existingInterview = state.interview.currentInterview;

    if (existingInterview && existingInterview.id === id) {
      return existingInterview;
    }

    try {
      const interview = await InterviewsAPI.getInterview(id);
      return interview;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch interview');
    }
  }
);

export const startInterview = createAsyncThunk(
  'interview/startInterview',
  async (id: number, { rejectWithValue }) => {
    try {
      const startResult = await InterviewsAPI.startInterview(id);
      console.log('Start interview result:', startResult);
      console.log('Audio data from backend:', startResult.audio_data);
      return startResult;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to start interview');
    }
  }
);

export const submitResponse = createAsyncThunk(
  'interview/submitResponse',
  async (data: { session_token: string; audio_data?: string }, { rejectWithValue }) => {
    try {
      const result = await InterviewsAPI.submitResponse(data);
      console.log("Submit response result:", result);
      console.log("Audio data from backend for next question:", result.audio_data);
      return result;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to submit response');
    }
  }
);

export const retryQuestion = createAsyncThunk(
  'interview/retryQuestion',
  async (session_token: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/interviews/session/${session_token}/retry-question`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to retry question');
      }

      const data = await response.json();
      console.log('Rephrased question response:', data);
      console.log('Audio data for rephrased question:', data.audio_data);
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to retry question');
    }
  }
);

// Create the slice
const interviewSlice = createSlice({
  name: 'interview',
  initialState,
  reducers: {
    clearCurrentInterview: (state) => {
      state.currentInterview = null;
      state.interviewSession = null;
      state.currentQuestion = '';
      state.currentResponse = null;
    },
    setCurrentQuestion: (state, action: PayloadAction<string>) => {
      state.currentQuestion = action.payload;
    },
    setAudioData: (state, action: PayloadAction<any>) => {
      if (state.interviewSession) {
        state.interviewSession.audio_data = action.payload;
      }
    },
    setWorkflowState: (state, action: PayloadAction<any>) => {
      if (state.interviewSession) {
        state.interviewSession.workflow_state = action.payload;
      }
    }
  },
  extraReducers: (builder) => {
    builder
      // Handle fetchUserInterviews
      .addCase(fetchUserInterviews.pending, (state) => {
        state.status = 'loading';
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserInterviews.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.loading = false;
        state.interviews = action.payload;
      })
      .addCase(fetchUserInterviews.rejected, (state, action) => {
        state.status = 'failed';
        state.loading = false;
        state.error = action.payload as string;
      })

      // Handle fetchInterview
      .addCase(fetchInterview.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchInterview.fulfilled, (state, action) => {
        state.loading = false;
        state.currentInterview = action.payload;
      })
      .addCase(fetchInterview.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Handle startInterview
      .addCase(startInterview.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(startInterview.fulfilled, (state, action) => {
        state.loading = false;
        state.interviewSession = action.payload;
        
        // Extract question text from the response
        let questionText = '';
        if (typeof action.payload.first_question === 'string') {
          questionText = action.payload.first_question;
        } else if (action.payload.first_question && typeof action.payload.first_question === 'object') {
          questionText = action.payload.first_question.question || 
                       JSON.stringify(action.payload.first_question);
        }
        
        state.currentQuestion = questionText;
      })
      .addCase(startInterview.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Handle submitResponse
      .addCase(submitResponse.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitResponse.fulfilled, (state, action) => {
        state.loading = false;
        state.currentResponse = action.payload;
        
        // Extract question text from the response
        if (!action.payload.is_completed) {
          let questionText = '';
          if (typeof action.payload.next_question === 'string') {
            questionText = action.payload.next_question;
          } else if (action.payload.next_question && typeof action.payload.next_question === 'object') {
            questionText = action.payload.next_question.question || 
                         JSON.stringify(action.payload.next_question);
          }
          
          state.currentQuestion = questionText;
        }
      })
      .addCase(submitResponse.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Handle retryQuestion
      .addCase(retryQuestion.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(retryQuestion.fulfilled, (state, action) => {
        state.loading = false;
        
        // Extract rephrased question text
        let questionText = '';
        if (typeof action.payload.rephrased_question === 'string') {
          questionText = action.payload.rephrased_question;
        } else if (action.payload.rephrased_question && typeof action.payload.rephrased_question === 'object') {
          questionText = action.payload.rephrased_question.question || 
                      JSON.stringify(action.payload.rephrased_question);
        }
        
        state.currentQuestion = questionText;
        if (state.interviewSession) {
          state.interviewSession.audio_data = action.payload.audio_data;
        }
      })
      .addCase(retryQuestion.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  }
});

// Export actions and reducer
export const { clearCurrentInterview, setCurrentQuestion, setAudioData, setWorkflowState } = interviewSlice.actions;
export default interviewSlice.reducer;
