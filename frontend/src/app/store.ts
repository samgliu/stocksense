import { authApi } from '@/features/auth/api';
import { authReducer } from '@/features/auth/store/slice';
import { configureStore } from '@reduxjs/toolkit';
import { stockApi } from '@/features/stock/api';
import { stockReducer } from '@/features/stock/store/slice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    stock: stockReducer,
    [authApi.reducerPath]: authApi.reducer,
    [stockApi.reducerPath]: stockApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(authApi.middleware, stockApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
