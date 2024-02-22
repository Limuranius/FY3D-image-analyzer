from scipy.optimize import minimize
import numpy as np


def func(x: np.ndarray):
    return (x[0] + 10) ** 2 + 5


x0 = np.array([0.])
res = minimize(func, x0)
print(res)
