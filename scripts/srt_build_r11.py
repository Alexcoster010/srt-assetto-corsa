from pathlib import Path
import shutil
P=Path(__file__).resolve().parents[1]
base=P/'release-r10/content/cars/srt27_prototype'
assert base.is_dir(), 'Build r10 first'
out=P/'release-r11/content/cars/srt27_prototype'
shutil.copytree(base,out,dirs_exist_ok=True)
shutil.copytree(P/'revisions/r11/content/cars/srt27_prototype',out,dirs_exist_ok=True)
print(out)
