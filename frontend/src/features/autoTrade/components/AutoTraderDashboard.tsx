import { AutoTraderCard } from './AutoTraderCard';
import { useAppSelector } from '@/hooks/useAppSelector';
import { useGetUserAutoTradeSubscriptionsQuery } from '../api';

export const AutoTraderDashboard = () => {
  const user_id = useAppSelector((state) => state.auth.id);
  const { data: subscriptions, isLoading } = useGetUserAutoTradeSubscriptionsQuery(user_id, {
    skip: !user_id,
  });

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-800">📈 TradeBot Subscriptions</h1>

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
