import scipy
import pandas as pd

mat = scipy.io.loadmat("Lucinda cut data4.mat")

data = mat["OUT"][0, 0]

# print(data["Phase442"])
# print(data.dtype)
cols = [('AOT', 'O'), ('ROT', 'O'), ('J_Day', 'O'), ('toc', 'O'), ('Lwn_FQ', 'O'), ('O3', 'O'), ('ASYM442', 'O'),
        ('ASYM668', 'O'), ('Phase442', 'O'), ('Phase668', 'O'), ('tinv', 'O'), ('SSA442', 'O'), ('SSA668', 'O'),
        ('tssa', 'O'), ('text', 'O'), ('tsat', 'O'), ('az', 'O'), ('senz', 'O'), ('solz', 'O'), ('W', 'O'), ('F0', 'O'),
        ('AOTExt442', 'O'), ('AOTExt668', 'O'), ('Phase_deg', 'O')]

values = dict()
for col, _ in cols:
    col_values = data[col]
    values[col] = col_values

print(1)