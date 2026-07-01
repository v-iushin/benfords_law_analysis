import math as m



def lead_digit(x):
    """Leading digit of number x"""
    x = abs(x)
    while x >= 10:
        x /= 10
    return int(x)

def values_digit(values, digits):
    """Make list using values for each leading digit"""
    values_dig = [lead_digit(value) for value in values]
    N = len(values_dig)
    counts = [values_dig.count(i) for i in digits]
    return counts, N

def benford(digits, N):
    """Theoretical Benford's value for specific total number of counts"""
    ben = [round(N * m.log10(1 + 1/d), 3) for d in digits]
    return ben

def chi_sq(values_dig, ben, digits):
    """Pearson chi-square statistic"""
    chi2 = sum([(values_dig[d-1] - ben[d-1])**2 / ben[d-1] for d in digits])
    chi2 = round(chi2, 2)
    return chi2

def magn(x):
    """
    1-9: 0
    10-99: 1
    100-999: 2
    ...
    """
    return int(m.log10(x))

def magnitude_order(values):
    """Orders of magnitude"""
    values = [abs(value) for value in values]
    magn_min = int(magn(min(values)))
    magn_max = int(magn(max(values)))
    magnitudes = list(range(magn_min, magn_max+1))
    magns_count = []
    for magnitude in magnitudes:
        magn_count = 0
        for value in values:
            if magn(value) == magnitude:
                magn_count += 1
        magns_count.append(magn_count)
    return magnitudes, magns_count

def sigma_log10(values):
    """Standart deviation of log_10(x)"""
    logs = [m.log10(abs(value)) for value in values]
    mean = sum(logs) / len(logs)
    sig = m.sqrt(sum((log - mean)**2 for log in logs) / len(logs))
    sig = round(sig, 2)
    return sig

def analyze(name, values, digits, color):
    """Analyze pipeline"""
    values_dig, N = values_digit(values, digits)
    ben = benford(digits, N)
    chi2 = chi_sq(values_dig, ben, digits)
    sigma = sigma_log10(values)
    magns, magns_count = magnitude_order(values)
    return {
        "name": name, "counts": values_dig, "N": N, "benford": ben,
        "chi_sq": chi2, "sigma": sigma,
        "magnitudes": magns, "magnitude_counts": magns_count,
        "color": color
    }
