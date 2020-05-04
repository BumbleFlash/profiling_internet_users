from scipy import stats
from resources.sqllite_modules import sqllite_core
import sqlite3
import math

db = sqlite3.connect("users.db")


def operations_each_window(file1, file2, window):
    n = n_value(file1, window)
    r1a2a = spearman_correlate(file1, file1, window, 1, 2)
    r1a2b = spearman_correlate(file1, file2, window, 1, 2)
    r2a2b = spearman_correlate(file1, file2, window, 2, 2)
    rm_square = root_mean_square(r1a2a, r1a2b)
    f = f_value(r2a2b, rm_square)
    h = h_value(f, rm_square)
    z1a2b = z_value_init(r1a2b)
    z1a2a = z_value_init(r1a2a)
    z = z_value_main(z1a2a, z1a2b, int(n), h, r2a2b)
    p = p_value(z)
    return p


def spearman_correlate(file1, file2, window, week1, week2):
    a = sqllite_core.get_split_ratio_data(file1, window, week1)
    b = sqllite_core.get_split_ratio_data(file2, window, week2)
    spearman_value = stats.spearmanr(a, b)
    return spearman_value.correlation


def root_mean_square(r1a2a, r1a2b):
    return (r1a2a ** 2 + r1a2b ** 2) / 2


def f_value(ra2b2, rm_square):
    num = 1 - ra2b2
    if rm_square == 1:
        rm_square = 0.999999999
    den = 2 * (1 - rm_square)
    return num / den


def h_value(f, rm_square):
    num = 1 - (f * rm_square)
    if rm_square == 1:
        rm_square = 0.99999999
    den = 1 - rm_square
    return num / den


def z_value_init(r):
    num = 1 + r
    if r == 1:
        r = 0.999999
    den = 1 - r
    return (math.log10(num / den)) / 2


def z_value_main(z1a2a, z1a2b, n, h, r2a2b):
    sqr_n = math.sqrt(n - 3)
    if r2a2b == 1:
        r2a2b = 0.99999999999
    den = 2 * (1 - r2a2b) * h
    return (z1a2a - z1a2b) * (sqr_n / den)


def n_value(file, window):
    return sqllite_core.get_window_count_week(file, window)


def p_value(z):
    p = 0.3275911
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    if z < 0.0:
        sign = -1
    else:
        sign = 1
    x = abs(z) / math.sqrt(2.0)
    t = 1.0 / (1.0 + p * x)
    erf = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    return 0.5 * (1.0 + sign * erf)
