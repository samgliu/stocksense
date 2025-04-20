import { StockInput } from '../components/StockInput';
import { StockResult } from '../components/StockResults';

export default function StockAnalyzePage() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-8 py-10">
      <h1 className="mb-2 text-2xl font-semibold tracking-tight text-blue-600">
        StockSense AI Analyzer
      </h1>

      <StockInput />
      <StockResult />
    </div>
  );
}
