const backendBase = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${backendBase}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`요청 실패: ${response.status}`);
  }

  return (await response.json()) as T;
}

export interface SignalPayload {
  symbol: string;
  score: number;
  tp_pct: number;
}

export interface SignalsResponse {
  signals: SignalPayload[];
}

export interface KisCredentialsStatus {
  has_credentials: boolean;
  appkey_preview: string;
  account_no8_preview: string;
  account_prod2_preview: string;
  is_paper: boolean;
}

export interface KisCredentialsRequest {
  appkey: string;
  appsecret: string;
  account_no8: string;
  account_prod2: string;
  is_paper: boolean;
}

export async function fetchSignals(): Promise<SignalsResponse> {
  try {
    return await fetchJson<SignalsResponse>("/api/signals/recent?limit=5");
  } catch (error) {
    return {
      signals: [
        { symbol: "AAPL", score: 0.72, tp_pct: 0.05 },
        { symbol: "TSLA", score: 0.65, tp_pct: 0.06 },
        { symbol: "NVDA", score: 0.81, tp_pct: 0.05 },
      ],
    };
  }
}

export async function fetchKisCredentialsStatus(): Promise<KisCredentialsStatus> {
  return await fetchJson<KisCredentialsStatus>("/api/admin/kis/credentials");
}

export async function saveKisCredentials(
  payload: KisCredentialsRequest,
): Promise<KisCredentialsStatus> {
  return await fetchJson<KisCredentialsStatus>("/api/admin/kis/credentials", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
