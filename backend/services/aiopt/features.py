"""Feature engineering helpers used for AI optimisation."""
from __future__ import annotations

from typing import Dict

import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a dataframe with engineered features for modelling."""

    features = pd.DataFrame(index=df.index)
    features["ret_5s"] = df["price"].pct_change(periods=5).fillna(0)
    features["ret_15s"] = df["price"].pct_change(periods=15).fillna(0)
    features["vol_spike"] = df["volume"].rolling(window=15, min_periods=1).mean()
    return features.fillna(0)
