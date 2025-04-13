import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { AutoTradeSubscription } from './types';
import { auth } from '@/features/auth/firebase';

export const autoTradeApi = createApi({
  reducerPath: 'autoTradeApi',
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
    subscribeToAutoTrade: builder.mutation<
      AutoTradeSubscription,
      Omit<AutoTradeSubscription, 'id' | 'created_at' | 'last_run_at' | 'active'>
    >({
      query: (body) => ({
        url: `/auto-trade/subscribe`,
        method: 'POST',
        body,
      }),
    }),
    updateAutoTradeSubscription: builder.mutation<
      AutoTradeSubscription,
      { id: string; updates: Partial<AutoTradeSubscription> }
    >({
      query: ({ id, updates }) => ({
        url: `/auto-trade/subscribe/${id}`,
        method: 'PUT',
        body: updates,
      }),
    }),
    deleteAutoTradeSubscription: builder.mutation<{ detail: string }, string>({
      query: (id) => ({
        url: `/auto-trade/subscribe/${id}`,
        method: 'DELETE',
      }),
    }),
    getUserAutoTradeSubscriptions: builder.query<AutoTradeSubscription[], string>({
      query: (user_id) => `/auto-trade/subscribe?user_id=${user_id}`,
    }),
    forceRunAutoTradeJob: builder.mutation<{ detail: string }, void>({
      query: () => ({
        url: `/auto-trade/force-run`,
        method: 'POST',
      }),
    }),
  }),
});

export const {
  useSubscribeToAutoTradeMutation,
  useUpdateAutoTradeSubscriptionMutation,
  useDeleteAutoTradeSubscriptionMutation,
  useGetUserAutoTradeSubscriptionsQuery,
  useForceRunAutoTradeJobMutation,
} = autoTradeApi;
