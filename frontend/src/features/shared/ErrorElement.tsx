import { Navigate, isRouteErrorResponse, useRouteError } from 'react-router';

export const ErrorElement = () => {
  const error = useRouteError();

  if (isRouteErrorResponse(error)) {
    if (error.status === 401) return <Navigate to="/signin" replace />;
    if (error.status === 404) return <Navigate to="/not-found" replace />;
  }

  return (
    <div className="flex h-screen items-center justify-center bg-gray-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-600">Oops!</h1>
        <p className="mt-2 text-xl text-gray-800">Something went wrong.</p>
        <p className="mt-4 text-sm text-gray-500">
          We encountered an error while processing your request. Please try again later.
        </p>
        <div className="mt-6">
          <a
            href="/"
            className="inline-block rounded-md bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
          >
            Go back to home
          </a>
        </div>
      </div>
    </div>
  );
};
