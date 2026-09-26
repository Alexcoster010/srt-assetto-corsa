"""Read-only surface configuration audit. It never edits a track."""
import argparse,configparser,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('track',type=Path);a=p.parse_args();out=[]
for f in sorted(a.track.rglob('surfaces.ini')):
 c=configparser.ConfigParser(strict=False,inline_comment_prefixes=(';',));c.read(f)
 for s in c.sections():
  if not s.startswith('SURFACE_'):continue
  row={k:c[s].get(k) for k in ['KEY','FRICTION','DIRT_ADDITIVE','IS_VALID_TRACK','DAMPING','WAV','VIBRATION_GAIN','SIN_HEIGHT']};row.update(file=str(f),section=s)
  grass=any(x in ((row['KEY'] or '')+' '+(row['WAV'] or '')).upper() for x in ['GRASS','GRS'])
  row['grass_named']=grass;row['flag']=None
  try:
   if grass and float(row['FRICTION'])>=.85:row['flag']='Grass-named surface has near-pavement friction; check intended mapping.'
  except (TypeError,ValueError):row['flag']='Friction unavailable.'
  out.append(row)
print(json.dumps({'track':str(a.track),'surfaces':out,'limits':'Names do not prove the collision mesh uses this surface. Packed data and CSP overrides may supersede these files. No grip judgment is possible from appearance alone.'},indent=2))
