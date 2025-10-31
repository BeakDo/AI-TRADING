"""Hazard modelling scaffold using lifelines."""
from __future__ import annotations

import numpy as np
from lifelines import CoxPHFitter
import pandas as pd


class HazardModel:
    def __init__(self, cph: CoxPHFitter) -> None:
        self._cph = cph

    def predict_partial_hazard(self, df: pd.DataFrame) -> np.ndarray:
        return self._cph.predict_partial_hazard(df).values


def train_hazard_model(df: pd.DataFrame, duration_col: str, event_col: str) -> HazardModel:
    cph = CoxPHFitter()
    cph.fit(df, duration_col=duration_col, event_col=event_col)
    return HazardModel(cph)
