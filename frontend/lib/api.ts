export async function fetchDummyData() {
  return {
    signals: [
      { symbol: "AAPL", score: 0.72, tp_pct: 0.05 },
      { symbol: "TSLA", score: 0.65, tp_pct: 0.06 },
      { symbol: "NVDA", score: 0.81, tp_pct: 0.05 },
    ],
  };
}
