import {
  useForceResetBalanceMutation,
  useForceRunAutoTradeJobMutation,
  useGetUserAutoTradeSubscriptionsQuery,
} from '../api';

import { AutoTraderCard } from './AutoTraderCard';
import { toast } from 'react-toastify';
import { useAppSelector } from '@/hooks/useAppSelector';
import { useEffect } from 'react';

export const AutoTraderDashboard = () => {
  const { id: user_id, role } = useAppSelector((state) => state.auth);
  const { data, isLoading, refetch } = useGetUserAutoTradeSubscriptionsQuery(user_id, {
    skip: !user_id,
  });

  const subscriptions = data?.subscriptions ?? [];
  const balance = data?.balance ?? 0;

  const [forceRunAutoTradeJob, { isLoading: isRunningRun }] = useForceRunAutoTradeJobMutation();
  const [forceResetBalance, { isLoading: isResetting }] = useForceResetBalanceMutation();

  const handleForceRun = async () => {
    try {
      const res = await forceRunAutoTradeJob().unwrap();
      toast.success(res.detail ?? 'Triggered AutoTrader run!');
    } catch {
      toast.error('Failed to force run.');
    }
  };

  const handleResetBalance = async () => {
    try {
      const res = await forceResetBalance().unwrap();
      toast.success(res.detail ?? 'Balance reset successfully!');
    } catch {
      toast.error('Failed to reset balance.');
    }
  };

  useEffect(() => {
    if (user_id) {
      refetch();
    }
  }, [user_id, refetch]);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-800">📈 AutoTrader Subscriptions</h1>
          {role === 'admin' && (
            <div className="flex gap-2">
              <button
                onClick={handleResetBalance}
                disabled={isResetting}
                className="cursor-pointer rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isResetting ? 'Resetting...' : 'Reset Balance'}
              </button>
              <button
                onClick={handleForceRun}
                disabled={isRunningRun}
                className="cursor-pointer rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isRunningRun ? 'Running...' : 'Force Run'}
              </button>
            </div>
          )}
        </div>

        <p className="mt-2 text-sm text-gray-600">
          💰 <strong>Balance:</strong> ${balance.toLocaleString()} &middot;
          <span className="ml-2 text-xs text-gray-400 italic">
            This is a simulation environment. Do not use for real trading decisions.
          </span>
        </p>
      </div>

      {isLoading && <p className="text-gray-500">Loading your subscriptions...</p>}
      {!isLoading && subscriptions.length === 0 && (
        <p className="text-gray-500">You have no active subscriptions.</p>
      )}

      <div className="space-y-4">
        {subscriptions.map((sub) => (
          <AutoTraderCard key={sub.id} subscription={sub} />
        ))}
      </div>
    </div>
  );
};
