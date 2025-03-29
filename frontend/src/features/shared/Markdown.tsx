import ReactMarkdown from 'react-markdown';

export const Markdown = ({ result }: { result: string }) => {
  return (
    <div className="prose prose-sm max-w-none text-gray-700">
      <ReactMarkdown>{result}</ReactMarkdown>
    </div>
  );
};
