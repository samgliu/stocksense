import { useEffect, useState } from 'react';
import {
  useForceResetBalanceMutation,
  useForceRunAutoTradeJobMutation,
  useGetUserAutoTradeSubscriptionsQuery,
} from '../api';

import { AutoTraderCard } from './AutoTraderCard';
import { ConfirmationDialog } from '@/features/shared/ConfirmationDialog';
import { toast } from 'react-toastify';
import { useAppSelector } from '@/hooks/useAppSelector';

export const AutoTraderDashboard = () => {
  const { id: user_id, role } = useAppSelector((state) => state.auth);
  const { data, isLoading, isFetching, refetch } = useGetUserAutoTradeSubscriptionsQuery(user_id, {
    skip: !user_id,
  });

  const subscriptions = data?.subscriptions ?? [];
  const balance = data?.balance ?? 0;
  const portfolioValue = data?.portfolio_value ?? 0;
  const totalValue = data?.total_value ?? 0;
  const totalReturn = data?.total_return ?? 0;
  const [confirmAction, setConfirmAction] = useState<null | (() => void)>(null);
  const [modalContent, setModalContent] = useState({ title: '', description: '' });
  const [forceRunAutoTradeJob, { isLoading: isRunningRun }] = useForceRunAutoTradeJobMutation();
  const [forceResetBalance, { isLoading: isResetting }] = useForceResetBalanceMutation();

  useEffect(() => {
    if (user_id) {
      refetch();
    }
  }, [user_id, refetch]);

  const format = (n: number) => `$${n.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;

  const activeSubs = subscriptions.filter((s) => s.active);
  const inactiveSubs = subscriptions.filter((s) => !s.active);

  if (!user_id || isLoading || isFetching) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 text-center text-gray-500">
        Loading SmartTrade dashboard...
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      {/* Header */}
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">📈 SmartTrade</h1>

        <div className="mt-3 flex gap-2 sm:mt-0">
          <button
            onClick={() => {
              setModalContent({
                title: 'Reset Balance',
                description: 'Are you sure you want to reset the balance for this account?',
              });
              setConfirmAction(() => async () => {
                try {
                  const res = await forceResetBalance().unwrap();
                  toast.success(res.detail ?? 'Balance reset.');
                } catch {
                  toast.error('Reset failed.');
                } finally {
                  setConfirmAction(null);
                }
              });
            }}
            disabled={isResetting}
            className="cursor-pointer rounded bg-gray-800 px-4 py-2 text-sm font-medium text-white hover:bg-black disabled:opacity-60"
          >
            {isResetting ? 'Resetting...' : 'Reset Balance'}
          </button>
          {role === 'admin' && (
            <button
              onClick={() => {
                setModalContent({
                  title: 'Trigger SmartTrade',
                  description: 'Do you want to force a SmartTrade job run now?',
                });
                setConfirmAction(() => async () => {
                  try {
                    const res = await forceRunAutoTradeJob().unwrap();
                    toast.success(res.detail ?? 'SmartTrade triggered!');
                  } catch {
                    toast.error('Force run failed.');
                  } finally {
                    setConfirmAction(null);
                  }
                });
              }}
              disabled={isRunningRun}
              className="cursor-pointer rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
            >
              {isRunningRun ? 'Running...' : 'Force Run'}
            </button>
          )}
        </div>
      </div>

      {/* Summary Card */}
      {!isLoading && !isFetching && (
        <div className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-200">
          <h2 className="mb-3 text-sm font-medium text-gray-500">Account Summary</h2>
          <div className="grid grid-cols-2 gap-4 text-[15px] sm:grid-cols-4">
            <div>
              <p className="text-xs text-gray-400">Cash</p>
              <p className="mt-1 font-semibold text-gray-900">{format(balance)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Invested</p>
              <p className="mt-1 font-semibold text-gray-900">{format(portfolioValue)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Total Value</p>
              <p className="mt-1 font-semibold text-gray-900">{format(totalValue)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Unrealized Gain</p>
              <p
                className={`mt-1 font-semibold ${
                  totalReturn > 0
                    ? 'text-green-600'
                    : totalReturn < 0
                      ? 'text-red-600'
                      : 'text-gray-800'
                }`}
              >
                {format(totalReturn)}
              </p>
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-400 italic">
            ⚠️ This is a simulation environment. Do not use for real investment decisions.
          </p>
        </div>
      )}

      {/* Subscriptions */}
      <div className="mt-8 space-y-6">
        {isLoading && <p className="text-gray-500">Loading your subscriptions...</p>}

        {/* Active */}
        {activeSubs.length > 0 && (
          <div>
            <h3 className="mb-2 text-sm font-medium text-gray-600">Active Subscriptions</h3>
            <div className="space-y-4">
              {activeSubs.map((sub) => (
                <AutoTraderCard key={sub.id} subscription={sub} />
              ))}
            </div>
          </div>
        )}

        {/* Inactive */}
        {inactiveSubs.length > 0 && (
          <div>
            <h3 className="mt-4 mb-2 text-sm font-medium text-gray-500">Inactive Subscriptions</h3>
            <div className="space-y-4 opacity-70">
              {inactiveSubs.map((sub) => (
                <AutoTraderCard key={sub.id} subscription={sub} isInactive />
              ))}
            </div>
          </div>
        )}

        {!isLoading && subscriptions.length === 0 && (
          <p className="text-gray-500">You have no SmartTrade subscriptions yet.</p>
        )}
        <ConfirmationDialog
          open={!!confirmAction}
          title={modalContent.title}
          description={modalContent.description}
          onConfirm={() => {
            if (confirmAction) confirmAction();
          }}
          onCancel={() => setConfirmAction(null)}
        />
      </div>
    </div>
  );
};
