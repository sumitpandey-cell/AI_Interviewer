import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { AuthAPI } from '@/lib/api';

interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: AuthAPI.isAuthenticated(), // Check localStorage for token
  loading: false,
  error: null
};

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async ({ email, password }: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const userData = await AuthAPI.login(email, password);
      console.log("User Login data", userData)
      return userData;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Login failed');
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (userData: { email: string; password: string; full_name: string }, { rejectWithValue }) => {
    try {
      const response = await AuthAPI.register(userData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Registration failed');
    }
  }
);

export const fetchUserInfo = createAsyncThunk(
  'auth/fetchUserInfo',
  async (_, { rejectWithValue }) => {
    try {
      if (!AuthAPI.isAuthenticated()) {
        throw new Error('Not authenticated');
      }
      
      const userInfo = await AuthAPI.getUserInfo();
      console.log("User data", userInfo)
      return userInfo;
    } catch (error: any) {
      // Try to get user info from token as fallback
      const tokenInfo = AuthAPI.getUserInfoFromToken();
      if (tokenInfo) {
        return tokenInfo;
      }
      return rejectWithValue(error.message || 'Failed to fetch user info');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      AuthAPI.logout();
      state.user = null;
      state.isAuthenticated = false;
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    }
  },
  extraReducers: (builder) => {
    builder
      // Handle login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        // We'll need to fetch user info separately
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Handle register
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
        state.isAuthenticated = true;
        // We'll need to fetch user info separately
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Handle fetchUserInfo
      .addCase(fetchUserInfo.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserInfo.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(fetchUserInfo.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        // If we can't get the user info, user is not authenticated
        if (!state.user) {
          state.isAuthenticated = false;
        }
      });
  }
});

export const { logout, setUser } = authSlice.actions;
export default authSlice.reducer;
