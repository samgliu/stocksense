import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const stockApi = createApi({
  reducerPath: 'stockApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${import.meta.env.VITE_BACKEND_URL}/api/v1/stock`,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('token');
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  endpoints: (builder) => ({
    analyzeStock: builder.mutation<{ summary: string }, string>({
      query: (text) => ({
        url: '/analyze',
        method: 'POST',
        body: { text },
      }),
    }),
  }),
});

export const { useAnalyzeStockMutation } = stockApi;
