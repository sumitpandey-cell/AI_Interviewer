import { configureStore } from '@reduxjs/toolkit';
import interviewReducer from '@/store/slices/interviewSlice';
import authReducer from '@/store/slices/authSlice';
import dashboardReducer from './slices/dashboardSlice';

export const store = configureStore({
  reducer: {
    interview: interviewReducer,
    auth: authReducer,
    dashboard: dashboardReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types (they may contain non-serializable data)
        ignoredActions: ['interview/setAudioData', 'interview/setWorkflowState'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
