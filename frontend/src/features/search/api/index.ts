import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { auth } from '@/features/auth/firebase';

export interface SemanticResult {
  id: string;
  name: string;
  ticker: string;
  summary: string | null;
  score: number;
}

export const searchApi = createApi({
  reducerPath: 'searchApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${import.meta.env.VITE_BACKEND_URL}/api/v1`,
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
    semanticSearch: builder.query<SemanticResult[], string>({
      query: (query) => `search/semantic-search?query=${encodeURIComponent(query)}`,
    }),
  }),
});

export const { useSemanticSearchQuery } = searchApi;
