# util functinos used in the main app

import numpy as np
import pandas as pd

def cal_vol(ts, window, offset=5):
    """
    The function calculates the realized volatility of a pandas Series object.

    Params:
        ts: pandas Series object, assumed to be daily close price.
        window: number of data points to calcualte std in return series.
        offset: number of day offsets to calculate return, defaulted to be weekly(5) return.

    Returns:
        vol: annualised historical volatility in a pd.Series format.
    """
    ret = np.log(ts / ts.shift(periods=offset)).dropna()
    vol = np.sqrt(252/offset) * ret.rolling(window).std().dropna()
    vol.name = ts.name + "-" + str(window) + "D-vol"

    return vol

def cal_var(ts, window, offset=5):
    """
    The function calculates the realized variance of a pandas Series object.

    Params:
        ts: pandas Series object, assumed to be daily close price.
        window: number of data points to calcualte variance in return series.
        offset: number of day offsets to calculate return, defaulted to be weekly(5) return.

    Returns:
        var: annualised historical variance in a pd.Series format.
    """
    ret = np.log(ts / ts.shift(periods=offset)).dropna()
    var = (252 / offset) * ret.rolling(window).var().dropna()
    var.name = ts.name + "-" + str(window) + "D-var"

    return var