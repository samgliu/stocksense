import { RootState } from '@/app/store';

export const selectAuth = (state: RootState) => state.auth;
export const selectUserEmail = (state: RootState) => state.auth.email;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;
