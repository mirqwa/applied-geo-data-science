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


def compute_geary_c(y, w):
    weight_values = list(w)
    y_std = y - y.mean()
    denominator = (y_std**2).sum()
    numerator = 0
    weight_sums = 0
    for i in range(len(y)):
        for j, weight in weight_values[i][1].items():
            numerator += weight * (y[i] - y[j]) ** 2
            weight_sums += weight
    geary_c = ((len(y) - 1) * numerator) / (2 * weight_sums * denominator)
    return geary_c
