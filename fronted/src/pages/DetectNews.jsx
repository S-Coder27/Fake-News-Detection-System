import { useState } from 'react';
import api from '../services/api';

export default function DetectNews() {
  const [headline, setHeadline] = useState('');
  const [text, setText] = useState('');
  const [res, setRes] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);

      const { data } = await api.post('/news/predict', {
        headline,
        text
      });

      setRes(data.data);
    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.message ||
        error.response?.data?.error ||
        'Prediction failed'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-5xl font-bold text-center mb-2">
        📰 Fake News Detector
      </h1>

      <p className="text-center text-slate-400 mb-8">
        AI Powered News Verification System
      </p>

      <form
        onSubmit={submit}
        className="bg-slate-800 border border-slate-700 rounded-3xl p-8 shadow-xl space-y-5"
      >
        <input
          type="text"
          placeholder="Enter Headline"
          value={headline}
          onChange={(e) => setHeadline(e.target.value)}
          className="w-full p-4 rounded-xl bg-slate-900 border border-slate-700"
        />

        <textarea
          placeholder="Paste full news article..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full p-4 rounded-xl bg-slate-900 border border-slate-700 min-h-[220px]"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full py-4 rounded-xl bg-blue-600 hover:bg-blue-700 font-bold text-lg"
        >
          {loading ? 'Analyzing...' : 'Detect News'}
        </button>
      </form>

      {res && (
        <div
          className={`mt-8 rounded-3xl p-8 border shadow-xl ${
            res.result === 'Real'
              ? 'bg-green-950 border-green-700'
              : 'bg-red-950 border-red-700'
          }`}
        >
          <h2 className="text-4xl font-bold mb-4">
            {res.result === 'Real'
              ? '✅ REAL NEWS'
              : '❌ FAKE NEWS'}
          </h2>

          <p className="mb-2">
            <strong>Confidence:</strong> {res.confidence}%
          </p>

          <p className="mb-2">
            <strong>Credibility Score:</strong>{' '}
            {res.credibilityScore}
          </p>

          {res.apiVerified !== undefined && (
            <>
              <p className="mb-2">
                <strong>API Verification:</strong>{' '}
                {res.apiVerified
                  ? '✅ Found in News Sources'
                  : '❌ Not Found'}
              </p>

              <p className="mb-2">
                <strong>Matching Articles:</strong>{' '}
                {res.matches}
              </p>
            </>
          )}

          {res.suspiciousKeywords?.length > 0 && (
            <div className="mt-4">
              <strong>Suspicious Keywords:</strong>

              <div className="flex flex-wrap gap-2 mt-2">
                {res.suspiciousKeywords.map((word, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-red-700 rounded-full text-sm"
                  >
                    {word}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 bg-slate-900 rounded-xl p-4">
            <h3 className="font-bold mb-2">
              AI Explanation
            </h3>

            <p className="text-slate-300">
              {res.explanation}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}