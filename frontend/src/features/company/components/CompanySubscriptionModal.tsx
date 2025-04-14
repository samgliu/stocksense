import { useState } from 'react';
import { useSubscribeToAutoTradeMutation } from '@/features/autoTrade/api';
import { useToast } from '@/hooks/useToast';

interface CompanySubscriptionModalProps {
  company_id: string;
  ticker: string;
  user_id: string;
  onClose: () => void;
}

export const CompanySubscriptionModal = ({
  company_id,
  ticker,
  user_id,
  onClose,
}: CompanySubscriptionModalProps) => {
  const toast = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [subscribeToAutoTrade] = useSubscribeToAutoTradeMutation();

  const [frequency, setFrequency] = useState<'hourly' | 'daily' | 'weekly'>('daily');
  const [riskTolerance, setRiskTolerance] = useState<'low' | 'medium' | 'high'>('medium');
  const [washSale, setWashSale] = useState(true);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await subscribeToAutoTrade({
        user_id,
        company_id,
        ticker,
        frequency,
        risk_tolerance: riskTolerance,
        wash_sale: washSale,
      }).unwrap();

      toast.success(`Subscribed ${ticker} to auto-trading!`);
      onClose();
    } catch {
      toast.error(`Failed to subscribe`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm transition-opacity duration-200">
      <div className="w-full max-w-md transform rounded-xl bg-white p-6 shadow-2xl transition-all duration-300 sm:w-[90%]">
        <h3 className="mb-4 text-lg font-semibold text-gray-800">Auto-Trade Setup</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Frequency</label>
            <select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value as 'hourly' | 'daily' | 'weekly')}
              className="mt-1 w-full rounded border p-2 text-sm"
              required
            >
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Risk Tolerance</label>
            <select
              value={riskTolerance}
              onChange={(e) => setRiskTolerance(e.target.value as 'low' | 'medium' | 'high')}
              className="mt-1 w-full rounded border p-2 text-sm"
              required
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              name="wash_sale"
              className="rounded border-gray-300"
              checked={washSale}
              onChange={(e) => setWashSale(e.target.checked)}
            />
            Enforce Wash Sale Rule
          </label>

          <div className="mt-6 flex justify-end space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="cursor-pointer rounded border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className={`cursor-pointer rounded px-4 py-2 text-sm font-medium text-white shadow ${
                isSubmitting ? 'cursor-not-allowed bg-gray-400' : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isSubmitting ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
