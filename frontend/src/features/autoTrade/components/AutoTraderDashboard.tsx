import { useForceRunAutoTradeJobMutation, useGetUserAutoTradeSubscriptionsQuery } from '../api';

import { AutoTraderCard } from './AutoTraderCard';
import { toast } from 'react-toastify';
import { useAppSelector } from '@/hooks/useAppSelector';

export const AutoTraderDashboard = () => {
  const { id: user_id, role } = useAppSelector((state) => state.auth);
  const { data: subscriptions, isLoading } = useGetUserAutoTradeSubscriptionsQuery(user_id, {
    skip: !user_id,
  });
  const [forceRunAutoTradeJob, { isLoading: isRunning }] = useForceRunAutoTradeJobMutation();

  const handleForceRun = async () => {
    try {
      const res = await forceRunAutoTradeJob().unwrap();
      toast.success(res.detail ?? 'Triggered AutoTrader run!');
    } catch {
      toast.error('Failed to force run.');
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">📈 TradeBot Subscriptions</h1>
        {role === 'admin' && (
          <button
            onClick={handleForceRun}
            disabled={isRunning}
            className="cursor-pointer rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isRunning ? 'Running...' : 'Force Run'}
          </button>
        )}
      </div>

      {isLoading && <p className="text-gray-500">Loading your subscriptions...</p>}
      {!isLoading && subscriptions?.length === 0 && (
        <p className="text-gray-500">You have no active subscriptions.</p>
      )}

      <div className="space-y-4">
        {subscriptions?.map((sub) => <AutoTraderCard key={sub.id} subscription={sub} />)}
      </div>
    </div>
  );
};
