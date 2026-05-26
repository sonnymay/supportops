export function LoadingState({ message }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-gray-600">
      <div className="w-10 h-10 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mb-4" />
      <p className="text-sm font-medium">{message || "Loading…"}</p>
      <p className="text-xs text-gray-500 mt-2 max-w-md text-center">
        The demo backend runs on Render's free tier and sleeps after 15 min of inactivity.
        First load after a nap can take up to a minute while the server wakes up.
      </p>
    </div>
  );
}

export function ErrorState({ error, onRetry }) {
  return (
    <div className="rounded-lg border border-red-300 bg-red-50 p-6 max-w-2xl">
      <p className="text-red-800 font-semibold mb-1">Couldn't load data</p>
      <p className="text-red-700 text-sm mb-4 break-words">{error}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition"
        >
          Retry
        </button>
      )}
    </div>
  );
}
