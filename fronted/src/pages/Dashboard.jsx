import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    total: 0,
    fake: 0,
    real: 0
  });

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const { data } = await api.get('/news/history');

      const predictions = data?.data?.predictions || [];

      const fakeCount = predictions.filter(
        item => item.result === 'Fake'
      ).length;

      const realCount = predictions.filter(
        item => item.result === 'Real'
      ).length;

      setStats({
        total: predictions.length,
        fake: fakeCount,
        real: realCount
      });

      setHistory(predictions);
    } catch (error) {
      console.error('Dashboard Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-8">
        <h1 className="text-4xl font-bold">Loading Dashboard...</h1>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">

      <h1 className="text-5xl font-bold mb-8">
        Dashboard
      </h1>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-3 gap-6 mb-10">

        <div className="bg-slate-800 border border-slate-700 rounded-3xl p-6">
          <h3 className="text-slate-400 mb-3">
            Total Predictions
          </h3>

          <p className="text-5xl font-bold">
            {stats.total}
          </p>

          <p className="text-slate-500 mt-2">
            Saved prediction history
          </p>
        </div>

        <div className="bg-red-950 border border-red-700 rounded-3xl p-6">
          <h3 className="text-red-300 mb-3">
            Fake News
          </h3>

          <p className="text-5xl font-bold">
            {stats.fake}
          </p>

          <p className="text-red-400 mt-2">
            Detected fake articles
          </p>
        </div>

        <div className="bg-green-950 border border-green-700 rounded-3xl p-6">
          <h3 className="text-green-300 mb-3">
            Real News
          </h3>

          <p className="text-5xl font-bold">
            {stats.real}
          </p>

          <p className="text-green-400 mt-2">
            Detected real articles
          </p>
        </div>
      </div>

      {/* Recent Predictions */}
      <div className="bg-slate-800 border border-slate-700 rounded-3xl p-6">

        <h2 className="text-2xl font-bold mb-6">
          Recent Predictions
        </h2>

        {history.length === 0 ? (
          <p className="text-slate-400">
            No predictions found.
          </p>
        ) : (
          <div className="space-y-4">
            {history.map((item) => (
              <div
                key={item.id}
                className="bg-slate-900 rounded-xl p-4 border border-slate-700"
              >
                <div className="flex justify-between items-center">

                  <div>
                    <h3 className="font-semibold">
                      {item.headline || 'Untitled News'}
                    </h3>

                    <p className="text-sm text-slate-400">
                      Confidence: {item.confidence}%
                    </p>
                  </div>

                  <span
                    className={`px-4 py-2 rounded-full font-bold ${
                      item.result === 'Fake'
                        ? 'bg-red-600'
                        : 'bg-green-600'
                    }`}
                  >
                    {item.result}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}