export function LoadingState({ message }) {
  return (
    <div role="status" className="flex flex-col items-center justify-center py-16 text-gray-600">
      <div
        aria-hidden="true"
        className="w-10 h-10 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mb-4"
      />
      <p className="text-sm font-medium">{message || "Loading…"}</p>
      <p className="text-xs text-gray-500 mt-2 max-w-md text-center">
        The service may need a moment to wake up after a period of inactivity.
      </p>
    </div>
  );
}

export function ErrorState({ error, onRetry }) {
  return (
    <div role="alert" className="rounded-lg border border-red-300 bg-red-50 p-5 max-w-2xl">
      <p className="text-red-900 font-semibold mb-1">SupportOps could not load this view</p>
      <p className="text-red-800 text-sm mb-4 break-words">{error}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function InlineError({ error }) {
  if (!error) return null;

  return (
    <p role="alert" className="mb-4 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
      {error}
    </p>
  );
}
