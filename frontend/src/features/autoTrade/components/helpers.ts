import { HoldingSummary, HoldingSummaryDisplay } from '../api/types';

export const titleCase = (str: string): string =>
  str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();

const format = (n: number) => `$${n.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;

export const formatValue = (val: number | null | undefined): string =>
  val === undefined || val === null || isNaN(val) ? 'N/A' : format(val);

export const holdingSummaryFormatter = (
  holdingSummary: HoldingSummary | undefined,
): HoldingSummaryDisplay | undefined => {
  if (!holdingSummary) return undefined;

  const format = (value: number | null): string =>
    value === null || isNaN(value) ? 'N/A' : value.toFixed(2);

  return {
    shares: format(holdingSummary.shares),
    average_cost: format(holdingSummary.average_cost),
    current_price: format(holdingSummary.current_price),
    market_value: format(holdingSummary.market_value),
    unrealized_gain: format(holdingSummary.unrealized_gain),
    gain_pct:
      holdingSummary.gain_pct === null || isNaN(holdingSummary.gain_pct)
        ? 'N/A'
        : `${holdingSummary.gain_pct.toFixed(2)}%`,
  };
};
