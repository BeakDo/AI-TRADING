"""AI 최적화를 위한 피처 엔지니어링 헬퍼."""
from __future__ import annotations

from typing import Dict

import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """모델링용으로 가공된 피처 데이터프레임을 반환한다."""

    features = pd.DataFrame(index=df.index)
    features["ret_5s"] = df["price"].pct_change(periods=5).fillna(0)
    features["ret_15s"] = df["price"].pct_change(periods=15).fillna(0)
    features["vol_spike"] = df["volume"].rolling(window=15, min_periods=1).mean()
    return features.fillna(0)
