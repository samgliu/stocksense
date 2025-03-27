import { setError, setLoading, setResult } from '../store/slice';

import { useAnalyzeStockMutation } from '@/features/stock/api';
import { useAppDispatch } from '@/hooks/useAppDispatch';
import { useState } from 'react';

export const StockInput = () => {
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [analyzeStock, { isLoading, reset }] = useAnalyzeStockMutation();
  const dispatch = useAppDispatch();

  const handleAnalyze = async () => {
    let inputText = text.trim();

    if (file) {
      const reader = new FileReader();
      reader.onload = async () => {
        const fileContent = reader.result as string;
        const combined = inputText ? `${inputText}\n\n${fileContent}` : fileContent;
        await analyze(combined);
      };
      reader.readAsText(file);
    } else if (inputText) {
      await analyze(inputText);
    }
  };

  const analyze = async (content: string) => {
    dispatch(setLoading(true));
    try {
      reset();
      const response = await analyzeStock(content).unwrap();
      dispatch(setResult(response.summary));
    } catch (err: any) {
      dispatch(setError('Failed to analyze stock input.'));
      console.error('Analyze failed:', err);
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] ?? null);
  };

  return (
    <div className="w-full space-y-4">
      <label className="block text-sm font-medium text-gray-700">
        Enter stock notes or upload a file:
      </label>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste stock summary, news, or financial notes..."
        className="w-full rounded-md border border-gray-300 p-4 text-sm text-gray-800 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
        rows={6}
      />

      <div className="flex items-center justify-between">
        <input
          type="file"
          accept=".txt,.csv,.pdf"
          onChange={handleFileChange}
          className="block text-sm text-gray-600 file:mr-4 file:rounded-md file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-blue-700 hover:file:bg-blue-100"
        />
        {file && (
          <span className="max-w-[50%] truncate text-sm text-gray-500">Selected: {file.name}</span>
        )}
      </div>

      <button
        disabled={!text && !file && isLoading}
        onClick={handleAnalyze}
        className="mt-2 inline-block cursor-pointer rounded-md bg-blue-600 px-5 py-2 text-sm font-medium text-white shadow transition hover:bg-blue-700"
      >
        Analyze
      </button>
    </div>
  );
};
