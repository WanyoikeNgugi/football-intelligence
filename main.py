import os

# check top level
for item in os.listdir('data/FPL/2025'):
    print(item)

# check one manager folder
managers = os.listdir('data/FPL/2025/managers')
print(f"\nTotal managers: {len(managers)}")

# check one manager's files
sample = managers[0]
print(f"\nFiles for manager {sample}:")
for f in os.listdir(f'data/FPL/2025/managers/{sample}'):
    print(f" {f}")