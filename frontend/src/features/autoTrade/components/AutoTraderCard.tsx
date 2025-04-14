import { AutoTradeSubscription } from '../api/types';
import { Link } from 'react-router-dom';
import { useDeleteAutoTradeSubscriptionMutation } from '../api';
import { useState } from 'react';
import { useToast } from '@/hooks/useToast';

export const AutoTraderCard = ({ subscription }: { subscription: AutoTradeSubscription }) => {
  const [deleteSub] = useDeleteAutoTradeSubscriptionMutation();
  const toast = useToast();
  const [showConfirm, setShowConfirm] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const handleDelete = async () => {
    try {
      await deleteSub(subscription.id).unwrap();
      toast.success('Subscription canceled.');
      setShowConfirm(false);
    } catch {
      toast.error('Failed to cancel subscription.');
    }
  };

  return (
    <div className="relative rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        {/* LEFT SIDE */}
        <div className="flex-1 space-y-1">
          <Link
            to={`/company/profile/${subscription.company_id}/${subscription.ticker}`}
            className="text-lg font-semibold text-blue-700 hover:underline"
          >
            {subscription.company_name || subscription.ticker}
            <span className="ml-1 text-sm text-gray-500">({subscription.ticker})</span>
          </Link>

          <p className="text-sm text-gray-600">
            <span className="capitalize">{subscription.frequency}</span> ·{' '}
            <span className="capitalize">{subscription.risk_tolerance}</span> risk ·{' '}
            {subscription.wash_sale ? 'Wash Sale Enabled' : 'Wash Sale Disabled'}
          </p>

          <div className="mt-2 space-y-0.5 text-xs text-gray-500">
            <p>
              📅 Subscribed:{' '}
              {new Date(subscription.created_at).toLocaleString(undefined, {
                dateStyle: 'short',
                timeStyle: 'short',
              })}
            </p>
            <p>
              ⏱️ Last Run:{' '}
              {subscription.transactions?.length
                ? new Date(
                    [...subscription.transactions].sort(
                      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
                    )[0].timestamp,
                  ).toLocaleString(undefined, {
                    dateStyle: 'short',
                    timeStyle: 'short',
                  })
                : 'Not yet run'}
            </p>
          </div>

          {(subscription.transactions ?? []).length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="mt-2 cursor-pointer text-sm text-blue-600 hover:underline"
            >
              {expanded ? 'Hide Trade History' : 'Show Trade History'}
            </button>
          )}
        </div>

        {/* RIGHT SIDE */}
        <div className="sm:text-right">
          <button
            onClick={() => setShowConfirm(true)}
            className="inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-100"
          >
            Cancel
          </button>
        </div>
      </div>

      {/* TRADE HISTORY */}
      {expanded && (subscription.transactions ?? []).length > 0 && (
        <div className="mt-4 rounded-md border border-gray-100 bg-gray-50 p-3">
          <h3 className="mb-2 text-sm font-semibold text-gray-700">📜 Trade History</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-gray-500">
                <tr>
                  <th className="py-1 pr-3 text-left">Action</th>
                  <th className="py-1 pr-3 text-left">Amount</th>
                  <th className="py-1 pr-3 text-left">Price</th>
                  <th className="py-1 text-left">Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {(subscription.transactions ?? []).map((tx) => (
                  <tr key={tx.id} className="border-t border-gray-200 text-gray-700">
                    <td className="py-1 pr-3 font-medium text-gray-800">
                      {tx.action.toUpperCase()}
                    </td>
                    <td className="py-1 pr-3">{tx.amount}</td>
                    <td className="py-1 pr-3">${tx.price.toFixed(2)}</td>
                    <td className="py-1 text-xs text-gray-500">
                      {new Date(tx.timestamp).toLocaleString(undefined, {
                        dateStyle: 'short',
                        timeStyle: 'short',
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* CONFIRM MODAL */}
      {showConfirm && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/30 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-lg bg-white p-5 shadow-lg">
            <p className="mb-4 text-sm text-gray-700">
              Cancel auto-trading for <strong>{subscription.ticker}</strong>?
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="rounded bg-gray-100 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-200"
              >
                Keep
              </button>
              <button
                onClick={handleDelete}
                className="rounded bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
