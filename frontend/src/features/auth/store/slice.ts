import { PayloadAction, createSlice } from '@reduxjs/toolkit';

export interface AuthState {
  isAuthenticated: boolean;
  name: string | null;
  email: string | null;
  token: string | null;
  loading: boolean;
  role: 'admin' | 'user' | null;
  usage: number | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  name: null,
  email: null,
  token: null,
  loading: true,
  role: null,
  usage: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setAuth: (state, action: PayloadAction<AuthState>) => {
      Object.assign(state, { ...action.payload, loading: false });
    },
    clearAuth: (state) => {
      Object.assign(state, {
        isAuthenticated: false,
        name: null,
        email: null,
        token: null,
        loading: false,
        role: null,
        usage: null,
      });
    },
  },
});

export const { setAuth, clearAuth } = authSlice.actions;
export const authReducer = authSlice.reducer;
