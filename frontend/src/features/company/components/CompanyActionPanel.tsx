interface Props {
  isAnalyzing: boolean;
  showStreamModal: boolean;
  isButtonsDisabled: boolean;
  onAnalyze: () => void;
  onAnalyzeStream: () => void;
  onAutoTrade: () => void;
  userId?: string;
  companyExists: boolean;
}

export const CompanyActionsPanel = ({
  isAnalyzing,
  showStreamModal,
  isButtonsDisabled,
  onAnalyze,
  onAnalyzeStream,
  onAutoTrade,
  userId,
  companyExists,
}: Props) => {
  const disabled = isAnalyzing || showStreamModal || isButtonsDisabled;
  return (
    <div className="flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-4">
        <button
          onClick={onAnalyze}
          disabled={disabled}
          className={`rounded px-4 py-2 text-white ${
            disabled
              ? 'cursor-not-allowed bg-gray-400'
              : 'cursor-pointer bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {disabled ? 'Analyzing...' : '🔍 Analyze Company'}
        </button>
        <button
          onClick={onAnalyzeStream}
          disabled={disabled}
          className={`rounded px-4 py-2 text-white ${
            disabled
              ? 'cursor-not-allowed bg-gray-400'
              : 'cursor-pointer bg-purple-600 hover:bg-purple-700'
          }`}
        >
          {disabled ? 'Analyzing & Streaming...' : '📡 Stream & Analyze'}
        </button>
      </div>
      <button
        onClick={onAutoTrade}
        className="cursor-pointer rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700"
        disabled={!userId || !companyExists}
      >
        📈 Auto-Trade
      </button>
    </div>
  );
};
