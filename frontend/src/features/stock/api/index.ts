import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { HistoryItem } from './types';
import { auth } from '@/features/auth/firebase';

export const stockApi = createApi({
  reducerPath: 'stockApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${import.meta.env.VITE_BACKEND_URL}/api/v1/stock`,
    prepareHeaders: async (headers) => {
      const user = auth.currentUser;
      if (user) {
        const token = await user.getIdToken();
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
    getHistory: builder.query<HistoryItem[], void>({
      query: () => '/history',
      keepUnusedDataFor: 0,
    }),
  }),
});

export const { useAnalyzeStockMutation, useGetHistoryQuery } = stockApi;
