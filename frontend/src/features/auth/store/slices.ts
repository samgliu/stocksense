import { PayloadAction, createSlice } from '@reduxjs/toolkit';

export interface AuthState {
  isAuthenticated: boolean;
  name: string | null;
  email: string | null;
  token: string | null;
  loading: boolean;
}

const initialState: AuthState = {
  isAuthenticated: false,
  name: null,
  email: null,
  token: null,
  loading: true,
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
      });
    },
  },
});

export const { setAuth, clearAuth } = authSlice.actions;
export const authReducer = authSlice.reducer;
