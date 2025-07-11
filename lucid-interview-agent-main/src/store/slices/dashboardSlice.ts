import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { AuthAPI } from '@/lib/api';
import { API_BASE_URL } from '@/lib/api';
import { InterviewsAPI } from '@/lib/api'; // Assuming this is a utility to get mock data

// Define types
interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  avatar_url?: string;
  is_active: boolean;
}

interface DashboardData {
  total_interviews: number;
  completed_interviews: number;
  average_score?: number;
  total_questions_answered: number;
}

interface DashboardState {
  userProfile: UserProfile | null;
  dashboardData: DashboardData | null;
  loading: boolean;
  error: string | null;
}

// Initial state
const initialState: DashboardState = {
  userProfile: null,
  dashboardData: null,
  loading: false,
  error: null
};

// Async thunks
export const fetchDashboardData = createAsyncThunk(
  'dashboard/fetchDashboardData',
  async (_, { rejectWithValue }) => {
    try {
      // Get user info
      const userInfo = await AuthAPI.getUserInfo();
      
      // Fetch interviews and calculate dashboard stats
      const interviews = await InterviewsAPI.getUserInterviews();
      console.log("Fetched interviews:", interviews);
      // Calculate dashboard metrics from interviews
      const completedInterviews = interviews.filter(interview => interview.status === 'completed');
      // Create dashboard data object
      const dashboardData: DashboardData = {
        total_interviews: interviews.length,
        completed_interviews: completedInterviews.length,
        average_score: completedInterviews.length > 0 
          ? completedInterviews.reduce((sum, interview) => sum + (interview.score || 0), 0) / completedInterviews.length 
          : 0,
        total_questions_answered: interviews.reduce((sum, interview) => sum + (interview.questions_answered || 0), 0)
      };
      
      console.log("Calculated dashboard data:", dashboardData);
      return { userInfo, dashboardData };
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch dashboard data');
    }
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    setUserProfile: (state, action: PayloadAction<UserProfile>) => {
      state.userProfile = action.payload;
    },
    setDashboardData: (state, action: PayloadAction<DashboardData>) => {
      state.dashboardData = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      // Handle fetchDashboardData
      .addCase(fetchDashboardData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboardData.fulfilled, (state, action) => {
        state.loading = false;
        state.userProfile = action.payload.userInfo;
        state.dashboardData = action.payload.dashboardData;
      })
      .addCase(fetchDashboardData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  }
});

export const { setUserProfile, setDashboardData } = dashboardSlice.actions;
export default dashboardSlice.reducer;
