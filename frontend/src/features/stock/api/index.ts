import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithErrorHandling } from '@/features/helpers';

import { HistoryItem } from './types';

export const stockApi = createApi({
  reducerPath: 'stockApi',
  baseQuery: baseQueryWithErrorHandling(`${import.meta.env.VITE_BACKEND_URL}/api/v1/stock`),
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
