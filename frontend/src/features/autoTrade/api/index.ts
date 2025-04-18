import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithErrorHandling } from '@/features/helpers';

import { AutoTradeSubscription } from './types';

export const autoTradeApi = createApi({
  reducerPath: 'autoTradeApi',
  baseQuery: baseQueryWithErrorHandling(`${import.meta.env.VITE_BACKEND_URL}/api/v1`),
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
    getUserAutoTradeSubscriptions: builder.query<
      {
        balance: number;
        portfolio_value: number;
        total_value: number;
        total_return: number;
        subscriptions: AutoTradeSubscription[];
      },
      void
    >({
      query: () => `/auto-trade/subscribe`,
    }),
    forceRunAutoTradeJob: builder.mutation<{ detail: string }, void>({
      query: () => ({
        url: `/auto-trade/force-run`,
        method: 'POST',
      }),
    }),
    forceResetBalance: builder.mutation<{ detail: string }, void>({
      query: () => ({
        url: `/auto-trade/reset`,
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
  useForceResetBalanceMutation,
} = autoTradeApi;
