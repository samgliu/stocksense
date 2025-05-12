import { holdingSummaryFormatter, titleCase } from './helpers';

import { useToast } from '@/hooks/useToast';
import { useState } from 'react';
import { Link } from 'react-router';
import { useDeleteAutoTradeSubscriptionMutation } from '../api';
import { AutoTradeSubscription } from '../api/types';

export const AutoTraderCard = ({
  subscription,
  isInactive = false,
}: {
  subscription: AutoTradeSubscription;
  isInactive?: boolean;
}) => {
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

  const summary = holdingSummaryFormatter(subscription.holding_summary);
  const gainColor =
    (subscription.holding_summary?.unrealized_gain ?? 0) > 0
      ? 'text-green-600'
      : (subscription.holding_summary?.unrealized_gain ?? 0) < 0
        ? 'text-red-600'
        : 'text-gray-700';

  return (
    <div className="relative rounded-xl border border-gray-200 bg-white p-5 text-xs shadow-sm transition hover:shadow-md sm:text-sm">
      {/* Cancel Button */}
      <div className="absolute top-4 right-4">
        {!isInactive && (
          <button
            onClick={() => setShowConfirm(true)}
            className="rounded-md border border-gray-300 bg-white px-3 py-1 text-xs text-gray-700 shadow-sm hover:bg-gray-100"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Header Info */}
      <div className="flex flex-col gap-3">
        <div>
          <Link
            to={`/company/profile/${subscription.company_id}/${subscription.ticker}`}
            className="text-base font-medium text-blue-700 hover:underline"
          >
            {subscription.company_name || subscription.ticker}
            <span className="ml-1 text-xs text-gray-500">({subscription.ticker})</span>
          </Link>
          <p className="text-gray-500">
            {titleCase(subscription.frequency)} · {titleCase(subscription.risk_tolerance)} risk ·{' '}
            {subscription.wash_sale ? 'Wash Sale Enabled' : 'Wash Sale Disabled'}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-y-1 text-[11px] text-gray-500">
          <span>
            📅 Subscribed:{' '}
            {new Date(subscription.created_at).toLocaleString(undefined, {
              dateStyle: 'short',
              timeStyle: 'short',
            })}
          </span>
          <span>
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
          </span>
        </div>

        {/* Holding Summary */}
        {summary && (
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
            <div className="grid grid-cols-2 gap-x-6 gap-y-2">
              <div>
                <p className="text-[11px] text-gray-400">Shares</p>
                <p className="text-gray-800">{summary.shares}</p>
              </div>
              <div>
                <p className="text-[11px] text-gray-400">Avg Cost</p>
                <p className="text-gray-800">{summary.average_cost}</p>
              </div>
              <div>
                <p className="text-[11px] text-gray-400">Current Price</p>
                <p className="text-gray-800">{summary.current_price}</p>
              </div>
              <div>
                <p className="text-[11px] text-gray-400">Market Value</p>
                <p className="text-gray-800">{summary.market_value}</p>
              </div>
              <div className="col-span-2">
                <p className="text-[11px] text-gray-400">Unrealized Gain</p>
                <p className={`font-medium ${gainColor}`}>
                  {summary.unrealized_gain} {summary.gain_pct}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Expand Trade History */}
        {(subscription.transactions ?? []).length > 0 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-2 text-xs text-blue-600 hover:underline"
          >
            {expanded ? 'Hide Trade History' : 'Show Trade History'}
          </button>
        )}
      </div>

      {/* Trade History Table */}
      {expanded && (subscription.transactions ?? []).length > 0 && (
        <div className="mt-4 rounded-md border border-gray-100 bg-gray-50 p-3">
          <h3 className="mb-2 text-xs font-medium text-gray-700">📜 Trade History</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
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
                    <td className="py-1 pr-3 font-medium">{tx.action.toUpperCase()}</td>
                    <td className="py-1 pr-3">{tx.amount}</td>
                    <td className="py-1 pr-3">${tx.price.toFixed(2)}</td>
                    <td className="py-1 text-gray-500">
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

      {/* Confirm Modal */}
      {showConfirm && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/30 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-lg bg-white p-5 text-sm shadow-lg">
            <p className="mb-4 text-gray-700">
              Cancel auto-trading for <strong>{subscription.ticker}</strong>?
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="rounded bg-gray-100 px-3 py-1.5 text-gray-700 hover:bg-gray-200"
              >
                Keep
              </button>
              <button
                onClick={handleDelete}
                className="rounded bg-red-600 px-3 py-1.5 text-white hover:bg-red-700"
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
