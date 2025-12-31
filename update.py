import os
import shutil


libdir = "C:/Users/Richa/AppData/Local/Programs/Python/Python312/Lib/site-packages/fmake"

src_dir = os.path.dirname(os.path.abspath(__file__))
src_dir +="/fmake"

for filename in os.listdir(src_dir):
    if filename.endswith('.py') and filename != os.path.basename(__file__):
        shutil.copy2(os.path.join(src_dir, filename), libdir)


