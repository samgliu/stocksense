import { StockInput } from '../components/StockInput';
import { StockResult } from '../components/StockResults';

export default function StockAnalyzePage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">StockSense AI Analyzer</h1>
      <StockInput />
      <StockResult />
    </div>
  );
}
