import os
import glob

html_files = [p for p in glob.glob('html/**', recursive=True) if os.path.isfile(p)]

print(len(html_files))
