export const formatCurrencyCompact = (value: number) =>
  `$${Intl.NumberFormat('en', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)}`;
