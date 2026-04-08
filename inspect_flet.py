import flet
print(f"version {flet.__version__}")
print('attrs with theme in name:')
for a in dir(flet):
    if 'theme' in a.lower():
        print(a)
