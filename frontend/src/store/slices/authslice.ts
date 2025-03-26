import { PayloadAction, createSlice } from '@reduxjs/toolkit';

interface AuthState {
  isAuthenticated: boolean;
  email: string | null;
  name: string | null;
  token: string | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  email: null,
  name: null,
  token: null,
};

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setAuth(state, action: PayloadAction<AuthState>) {
      Object.assign(state, action.payload);
    },
    clearAuth(state) {
      Object.assign(state, initialState);
    },
  },
});

export const { setAuth, clearAuth } = authSlice.actions;
export const authReducer = authSlice.reducer;
