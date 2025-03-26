import { authApi } from '@/features/auth/api';
import { authReducer } from '@/features/auth/store/slices';
import { configureStore } from '@reduxjs/toolkit';
import { stockReducer } from '@/features/stock/store/slices';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    stock: stockReducer,
    [authApi.reducerPath]: authApi.reducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(authApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
