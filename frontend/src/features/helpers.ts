import { fetchBaseQuery, BaseQueryFn, FetchBaseQueryError } from '@reduxjs/toolkit/query';
import * as Sentry from '@sentry/react';
import { auth } from '@/features/auth/firebase';

export const baseQueryWithErrorHandling = (
  baseUrl: string,
): BaseQueryFn<any, unknown, FetchBaseQueryError> => {
  const baseQuery = fetchBaseQuery({
    baseUrl,
    prepareHeaders: async (headers) => {
      const user = auth.currentUser;
      if (user) {
        const token = await user.getIdToken();
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  });
  return async (args, api, extraOptions) => {
    const result = await baseQuery(args, api, extraOptions);
    if (result.error && !(result.error.status === 401 || result.error.status === 403)) {
      Sentry.captureException(result.error);
    }
    return result;
  };
};
