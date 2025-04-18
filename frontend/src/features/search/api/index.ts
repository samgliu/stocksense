import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithErrorHandling } from '@/features/helpers';

export interface SemanticResult {
  id: string;
  name: string;
  ticker: string;
  summary?: string;
  sector?: string;
  industry?: string;
  domain?: string;
  score: number;
}

export const searchApi = createApi({
  reducerPath: 'searchApi',
  baseQuery: baseQueryWithErrorHandling(`${import.meta.env.VITE_BACKEND_URL}/api/v1`),
  endpoints: (builder) => ({
    semanticSearch: builder.query<SemanticResult[], string>({
      query: (query) => `search/semantic-search?query=${encodeURIComponent(query)}`,
    }),
  }),
});

export const { useSemanticSearchQuery } = searchApi;
