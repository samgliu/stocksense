import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { BackendUser } from '../store/types';
import { auth } from '../firebase';

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${import.meta.env.VITE_BACKEND_URL}/api/v1/auth/auth`,
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
    verifyToken: builder.query<BackendUser, void>({
      query: () => '/auth',
    }),
  }),
});

export const { useVerifyTokenQuery } = authApi;
