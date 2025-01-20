import libpysal
import numpy as np
from esda.moran import Moran
from pysal.lib import weights


def compute_moran_index(y, w):
    y_std = y - y.mean()
    weight_values = list(w)
    numerator = 0
    denominator = (y_std**2).sum()
    weight_sums = 0
    for i in range(len(y)):
        for j, weight in weight_values[i][1].items():
            numerator += weight * y_std[i] * y_std[int(j) - 1]
            weight_sums += weight
    moran_index = (len(y) * numerator) / (weight_sums * denominator)
    return moran_index


if __name__ == "__main__":
    w = libpysal.io.open(libpysal.examples.get_path("stl.gal")).read()
    f = libpysal.io.open(libpysal.examples.get_path("stl_hom.txt"))
    y = np.array(f.by_col["HR8893"])
    mi = Moran(y, w)
    moran_index = compute_moran_index(y, w)
