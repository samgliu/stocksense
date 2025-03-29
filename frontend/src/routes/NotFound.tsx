export const NotFound = () => {
  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center px-4 text-center">
      <div className="max-w-md">
        <h1 className="text-4xl font-bold text-gray-800 sm:text-5xl">404</h1>
        <p className="mt-2 text-lg text-gray-600">
          Sorry, the page you are looking for could not be found.
        </p>
        <a
          href="/"
          className="mt-6 inline-block rounded-md bg-blue-600 px-5 py-2 text-sm font-medium text-white shadow transition hover:bg-blue-700"
        >
          Go back to homepage
        </a>
      </div>
    </div>
  );
};
