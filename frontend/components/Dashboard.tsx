"use client";
import { FormEvent, useEffect, useState } from "react";
import {
  fetchKisCredentialsStatus,
  fetchSignals,
  saveKisCredentials,
  KisCredentialsRequest,
  KisCredentialsStatus,
  SignalPayload,
} from "../lib/api";

const initialCredentials: KisCredentialsRequest = {
  appkey: "",
  appsecret: "",
  account_no8: "",
  account_prod2: "",
  is_paper: true,
};

export default function Dashboard() {
  const [signals, setSignals] = useState<SignalPayload[]>([]);
  const [tradingEnabled, setTradingEnabled] = useState(true);
  const [credentials, setCredentials] = useState<KisCredentialsRequest>(
    initialCredentials,
  );
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [storedStatus, setStoredStatus] = useState<KisCredentialsStatus | null>(
    null,
  );

  useEffect(() => {
    fetchSignals().then((data) => setSignals(data.signals));
    fetchKisCredentialsStatus()
      .then((data) => {
        setStoredStatus(data);
        setCredentials((prev) => ({ ...prev, is_paper: data.is_paper }));
      })
      .catch(() => {
        setStoredStatus(null);
      });
  }, []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    try {
      const saved = await saveKisCredentials(credentials);
      setStoredStatus(saved);
      setStatus("KIS API 키가 안전하게 저장되었습니다.");
      setCredentials((prev) => ({ ...prev, appsecret: "" }));
    } catch (error) {
      setStatus("저장 중 오류가 발생했습니다. 정보를 다시 확인해주세요.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6">
      <header className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <h1 className="text-2xl font-semibold">AI 급등 레이더</h1>
        <button
          className={`px-4 py-2 rounded font-medium transition ${
            tradingEnabled ? "bg-emerald-500 hover:bg-emerald-400" : "bg-rose-500 hover:bg-rose-400"
          }`}
          onClick={() => setTradingEnabled((prev) => !prev)}
        >
          거래 {tradingEnabled ? "활성" : "중지"}
        </button>
      </header>
      <section className="grid gap-4 md:grid-cols-2">
        <div className="bg-slate-900 rounded p-4 shadow">
          <h2 className="font-medium mb-2">실시간 급등 감시</h2>
          <p className="text-sm text-slate-400 mb-3">
            최신 급등 점수와 목표 수익률을 실시간으로 확인합니다.
          </p>
          <ul className="space-y-2">
            {signals.map((signal) => (
              <li
                key={signal.symbol}
                className="flex justify-between bg-slate-800 rounded px-3 py-2"
              >
                <span className="font-medium">{signal.symbol}</span>
                <span className="text-emerald-400">
                  {(signal.score * 100).toFixed(1)}%
                </span>
                <span className="text-sm text-slate-400">
                  목표 {(signal.tp_pct * 100).toFixed(1)}%
                </span>
              </li>
            ))}
            {signals.length === 0 && (
              <li className="text-sm text-slate-500">표시할 급등 후보가 없습니다.</li>
            )}
          </ul>
        </div>
        <div className="bg-slate-900 rounded p-4 shadow space-y-2">
          <h2 className="font-medium">리스크 패널</h2>
          <p>일중 손실 한도: $500</p>
          <p>동시 보유 가능 종목: 3</p>
          <p className="text-sm text-slate-400">
            거래 토글은 백엔드 연결 후 실제 전략 루프 제어에 사용됩니다.
          </p>
        </div>
      </section>
      <section className="bg-slate-900 rounded p-4 shadow space-y-4">
        <div>
          <h2 className="font-medium">KIS API 자격 증명 관리</h2>
          <p className="text-sm text-slate-400">
            웹에서 입력한 키는 서버 측 안전한 파일에 저장되며 백엔드 설정이 자동으로 갱신됩니다.
          </p>
        </div>
        {storedStatus && (
          <div className="text-sm text-slate-300 space-y-1">
            <p>
              저장 상태:{" "}
              <span className="font-semibold text-emerald-400">
                {storedStatus.has_credentials ? "설정 완료" : "미설정"}
              </span>
            </p>
            {storedStatus.has_credentials && (
              <ul className="space-y-1">
                <li>앱 키: {storedStatus.appkey_preview || "-"}</li>
                <li>계좌 구분: {storedStatus.account_no8_preview || "-"}</li>
                <li>상품 코드: {storedStatus.account_prod2_preview || "-"}</li>
                <li>모의 투자 여부: {storedStatus.is_paper ? "모의" : "실전"}</li>
              </ul>
            )}
          </div>
        )}
        <form className="grid gap-3 md:grid-cols-2" onSubmit={handleSubmit}>
          <label className="flex flex-col gap-1 text-sm">
            <span>앱 키</span>
            <input
              type="text"
              required
              value={credentials.appkey}
              onChange={(event) =>
                setCredentials((prev) => ({ ...prev, appkey: event.target.value }))
              }
              className="rounded bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              placeholder="발급받은 APP KEY"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>앱 시크릿</span>
            <input
              type="password"
              required
              value={credentials.appsecret}
              onChange={(event) =>
                setCredentials((prev) => ({ ...prev, appsecret: event.target.value }))
              }
              className="rounded bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              placeholder="발급받은 APP SECRET"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>계좌 구분 8자리</span>
            <input
              type="text"
              required
              value={credentials.account_no8}
              onChange={(event) =>
                setCredentials((prev) => ({ ...prev, account_no8: event.target.value }))
              }
              className="rounded bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              placeholder="########"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>상품 코드 2자리</span>
            <input
              type="text"
              required
              value={credentials.account_prod2}
              onChange={(event) =>
                setCredentials((prev) => ({ ...prev, account_prod2: event.target.value }))
              }
              className="rounded bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              placeholder="##"
            />
          </label>
          <label className="flex items-center gap-2 text-sm md:col-span-2">
            <input
              type="checkbox"
              checked={credentials.is_paper}
              onChange={(event) =>
                setCredentials((prev) => ({ ...prev, is_paper: event.target.checked }))
              }
              className="h-4 w-4"
            />
            모의 투자(체크 해제 시 실전 모드)
          </label>
          <div className="md:col-span-2 flex items-center gap-3">
            <button
              type="submit"
              disabled={loading}
              className="bg-emerald-500 hover:bg-emerald-400 disabled:opacity-60 rounded px-4 py-2 font-medium"
            >
              {loading ? "저장 중..." : "자격 증명 저장"}
            </button>
            {status && <span className="text-sm text-slate-300">{status}</span>}
          </div>
        </form>
      </section>
    </main>
  );
}
