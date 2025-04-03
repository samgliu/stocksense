import type { CompanyNews } from '../api/types';

export const CompanyNewsComponent = ({
  news,
  isLoading,
}: {
  news?: CompanyNews[];
  isLoading: boolean;
}) => {
  if (isLoading) return <div className="text-sm text-gray-500">Loading news...</div>;
  if (!news?.length) return null;

  return (
    <div className="space-y-4">
      {news.map((item) => (
        <a
          key={item.url}
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="group flex gap-4 rounded-xl border border-gray-200 p-4 shadow-sm transition hover:bg-gray-50 hover:shadow-md"
        >
          {item.image_url && (
            <img
              src={item.image_url}
              alt={item.title}
              className="h-20 w-20 flex-shrink-0 rounded-md object-cover"
            />
          )}

          <div className="flex-1">
            <h3 className="text-md font-medium text-gray-900 group-hover:text-blue-600">
              {item.title}
            </h3>
            <p className="mt-1 line-clamp-2 text-sm text-gray-600">
              {item.snippet || item.description}
            </p>
            <p className="mt-2 text-xs text-gray-400">
              {new Date(item.published_at).toLocaleString()} &bull; {item.source}
            </p>
          </div>
        </a>
      ))}
    </div>
  );
};
