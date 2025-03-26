import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { BackendUser } from '../store/types';

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8000/api',
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
      query: () => '/protected',
    }),
  }),
});

export const { useVerifyTokenQuery } = authApi;
