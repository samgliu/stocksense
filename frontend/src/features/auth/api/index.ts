import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { BackendUser } from '../store/types';

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${import.meta.env.VITE_BACKEND_URL}/api/v1/auth/auth`,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('token');
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  endpoints: (builder) => ({
    verifyToken: builder.query<BackendUser, void>({
      query: () => '/auth',
    }),
  }),
});

export const { useVerifyTokenQuery } = authApi;
