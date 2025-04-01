import { authApi } from '@/features/auth/api';
import { authReducer } from '@/features/auth/store/slice';
import { companyApi } from '@/features/company/api';
import { configureStore } from '@reduxjs/toolkit';
import { dashboardApi } from '@/features/dashboard/api';
import { searchApi } from '@/features/search/api';
import { stockApi } from '@/features/stock/api';
import { stockReducer } from '@/features/stock/store/slice';
import { toastReducer } from '@/features/toast/store/slice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    stock: stockReducer,
    toast: toastReducer,
    [authApi.reducerPath]: authApi.reducer,
    [stockApi.reducerPath]: stockApi.reducer,
    [dashboardApi.reducerPath]: dashboardApi.reducer,
    [searchApi.reducerPath]: searchApi.reducer,
    [companyApi.reducerPath]: companyApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      authApi.middleware,
      stockApi.middleware,
      dashboardApi.middleware,
      searchApi.middleware,
      companyApi.middleware,
    ),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
