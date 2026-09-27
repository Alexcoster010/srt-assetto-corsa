from pathlib import Path
import shutil
P=Path(__file__).resolve().parents[1]
base=P/'release-r12/content/cars/srt27_prototype'
assert base.is_dir(), 'Build r12 first'
out=P/'release-r13/content/cars/srt27_prototype'
shutil.copytree(base,out,dirs_exist_ok=True)
shutil.copytree(P/'revisions/r13/content/cars/srt27_prototype',out,dirs_exist_ok=True)
print(out)
