import pandas as pd
import pytest
import numpy as np

from src.tests.base_test import BaseTest
from src.feature_engineering import get_sys_bp, get_dias_bp, calc_map

class TestFE(BaseTest):
    """Test Feature Engineering Functions"""

    def test_sys(self, load_abp):
        df = load_abp

        sys = get_sys_bp(df)

        assert len(sys) == 2
        assert sys == [(70, 100.8), (156, 95.2)]

    def test_bp(self, load_abp):
        df = load_abp

        dias = get_dias_bp(df)

        assert len(dias) == 2
        assert dias == [(54, 48.8), (139, 48.8)]

    def test_map(self, load_abp):
        df = load_abp

        sys = get_sys_bp(df)
        dias = get_dias_bp(df)

        indices, maps = calc_map(sys, dias)

        assert len(maps) == 2
        assert np.allclose(maps, np.array([66.13333333, 64.26666667]))
