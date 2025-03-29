import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { auth } from '@/features/auth/firebase';

export interface CompanyData {
  id: string;
  ticker: string;
  name: string;
  shortname?: string;
  current_price?: number;
  market_cap?: number;
  summary?: string;
  image?: string;
  sector?: string;
  industry?: string;
  website?: string;
  ceo?: string;
  ipo_date?: string;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
  phone?: string;
  exchange?: string;
  country?: string;
  fulltime_employees?: number;
}

export const companyApi = createApi({
  reducerPath: 'companyApi',
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
    getCompanyById: builder.query<CompanyData, { id: string; ticker: string }>({
      query: ({ id, ticker }) => `/companies/${id}/${ticker}`,
    }),
  }),
});

export const { useGetCompanyByIdQuery } = companyApi;
