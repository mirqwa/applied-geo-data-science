import libpysal
import numpy as np
from esda.moran import Moran


def compute_moran_index(y, w):
    y_std = y - y.mean()
    weight_values = list(w)
    numerator = 0
    denominator = (y_std**2).sum()
    weight_sums = 0
    for i in range(len(y)):
        for j, weight in weight_values[i][1].items():
            numerator += weight * y_std[i] * y_std[j]
            weight_sums += weight
    moran_index = (len(y) * numerator) / (weight_sums * denominator)
    return moran_index
