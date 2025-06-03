import numpy as np
import pandas as pd
def make_serializable(val):
    # Handle both numpy and plain python nan/inf
    if pd.isna(val) or val in [float('inf'), float('-inf'), np.inf, -np.inf]:
        return None
    if isinstance(val, (np.generic,)):
        return val.item()
    return val