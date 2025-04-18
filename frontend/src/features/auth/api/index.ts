import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithErrorHandling } from '@/features/helpers';

import { BackendUser } from '../store/types';

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: baseQueryWithErrorHandling(`${import.meta.env.VITE_BACKEND_URL}/api/v1/auth`),
  endpoints: (builder) => ({
    verifyToken: builder.query<BackendUser, void>({
      query: () => '/auth',
      keepUnusedDataFor: 0,
    }),
  }),
});

export const { useVerifyTokenQuery, useLazyVerifyTokenQuery } = authApi;
