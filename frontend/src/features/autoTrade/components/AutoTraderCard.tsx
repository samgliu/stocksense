import { AutoTradeSubscription } from '../api/types';
import { Link } from 'react-router-dom';
import { useDeleteAutoTradeSubscriptionMutation } from '../api';
import { useState } from 'react';
import { useToast } from '@/hooks/useToast';

export const AutoTraderCard = ({ subscription }: { subscription: AutoTradeSubscription }) => {
  const [deleteSub] = useDeleteAutoTradeSubscriptionMutation();
  const toast = useToast();
  const [showConfirm, setShowConfirm] = useState(false);

  const handleDelete = async () => {
    try {
      await deleteSub(subscription.id).unwrap();
      toast.success('AutoTrader subscription canceled.');
      setShowConfirm(false);
    } catch {
      toast.error('Failed to cancel subscription.');
    }
  };

  return (
    <div className="relative rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        {/* LEFT SIDE */}
        <div className="space-y-1">
          <Link
            to={`/company/profile/${subscription.company_id}/${subscription.ticker}`}
            className="cursor-pointer text-lg font-semibold text-blue-700 hover:underline"
          >
            {subscription.company_name || subscription.ticker}
            <span className="ml-1 text-sm text-gray-500">({subscription.ticker})</span>
          </Link>

          <p className="text-sm text-gray-600">
            <span className="capitalize">{subscription.frequency}</span> ·{' '}
            <span className="capitalize">{subscription.risk_tolerance}</span> risk ·{' '}
            {subscription.wash_sale ? 'Wash Sale Rule Enforced' : 'Wash Sale Rule Ignored'}{' '}
          </p>

          <div className="mt-2 space-y-1 text-xs text-gray-500">
            <p>
              📅 Subscribed:{' '}
              {new Date(subscription.created_at).toLocaleString(undefined, {
                dateStyle: 'short',
                timeStyle: 'short',
              })}
            </p>
            <p>
              ⏱️ Last Run:{' '}
              {subscription.last_run_at
                ? new Date(subscription.last_run_at).toLocaleString(undefined, {
                    dateStyle: 'short',
                    timeStyle: 'short',
                  })
                : 'Not yet run'}
            </p>
          </div>
        </div>

        {/* RIGHT SIDE */}
        <div className="flex shrink-0 items-center">
          <button
            onClick={() => setShowConfirm(true)}
            className="inline-flex cursor-pointer items-center gap-1 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-100"
          >
            Cancel
          </button>
        </div>
      </div>

      {/* CONFIRM MODAL */}
      {showConfirm && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-xs rounded-lg bg-white p-4 shadow-md">
            <p className="mb-4 text-sm text-gray-700">
              Are you sure you want to cancel auto-trading for{' '}
              <strong>{subscription.ticker}</strong>?
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="cursor-pointer rounded bg-gray-100 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-200"
              >
                No, Keep
              </button>
              <button
                onClick={handleDelete}
                className="cursor-pointer rounded bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700"
              >
                Yes, Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
