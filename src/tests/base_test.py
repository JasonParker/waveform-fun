import pandas as pd
import numpy as np
import pytest

from src.utils.utils import get_fn

class BaseTest:

    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        tmpdir.chdir()

    @pytest.fixture()
    def load_abp(self):
        df = pd.read_csv(get_fn("abp.csv"))

        return df
