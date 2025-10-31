"use client";
import { useEffect, useState } from "react";
import { fetchDummyData } from "../lib/api";

interface Signal {
  symbol: string;
  score: number;
  tp_pct: number;
}

export default function Dashboard() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [tradingEnabled, setTradingEnabled] = useState(true);

  useEffect(() => {
    fetchDummyData().then((data) => setSignals(data.signals));
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6">
      <header className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">AI Surge Radar</h1>
        <button
          className={`px-4 py-2 rounded ${
            tradingEnabled ? "bg-emerald-500" : "bg-rose-500"
          }`}
          onClick={() => setTradingEnabled((prev) => !prev)}
        >
          Trading {tradingEnabled ? "Enabled" : "Disabled"}
        </button>
      </header>
      <section className="grid gap-4 md:grid-cols-2">
        <div className="bg-slate-900 rounded p-4">
          <h2 className="font-medium mb-2">Surge Radar</h2>
          <ul className="space-y-2">
            {signals.map((signal) => (
              <li
                key={signal.symbol}
                className="flex justify-between bg-slate-800 rounded px-3 py-2"
              >
                <span>{signal.symbol}</span>
                <span className="text-emerald-400">
                  {(signal.score * 100).toFixed(1)}%
                </span>
                <span className="text-sm text-slate-400">
                  TP {(signal.tp_pct * 100).toFixed(1)}%
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-slate-900 rounded p-4">
          <h2 className="font-medium mb-2">Risk Panel</h2>
          <p>Daily Drawdown Limit: $500</p>
          <p>Max Concurrent Positions: 3</p>
        </div>
      </section>
    </main>
  );
}
