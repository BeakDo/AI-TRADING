import asyncio

import pytest

from backend.services.signal.surge import SurgeDetector


def test_surge_detector_entry():
    detector = SurgeDetector(entry_threshold=0.6, vol_spike_threshold=3.0)
    features = {"ret_5s": 0.05, "ret_15s": 0.02, "vol_spike": 4.0}
    signal = detector.score("AAPL", features)
    assert detector.is_entry(signal)
