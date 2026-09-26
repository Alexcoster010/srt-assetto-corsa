"""Summarize SRT diagnostics without mistaking idle samples for a wheel test."""
import argparse,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('log',type=Path);p.add_argument('--out',type=Path);a=p.parse_args();rows=[];meta={}
for line in a.log.read_text().splitlines():
 try:r=json.loads(line)
 except ValueError:continue
 if 'schema' in r:meta=r
 elif isinstance(r.get('SpeedKMH'),(int,float)):rows.append(r)
moving=[r for r in rows if r['SpeedKMH']>=20 and abs(r.get('Steer') or 0)>.03 and isinstance(r.get('LastFF'),(int,float))]
forces=[abs(r['LastFF']) for r in moving];braking=[r for r in rows if r['SpeedKMH']>=20 and (r.get('Brake') or 0)>.2]
result={'metadata':meta,'samples':len(rows),'moving_corner_samples':len(moving),'braking_samples':len(braking),'ffb_test':'insufficient moving corner data' if len(moving)<100 else ('zero or near-zero game FFB: investigate car and game settings' if max(forces)<.001 else 'nonzero game FFB observed; physical wheel response remains unverified'),'peak_absolute_game_ffb':max(forces) if forces else None,'fraction_over_0_98':sum(f>=.98 for f in forces)/len(forces) if forces else None,'limits':['LastFF is normalized game output, not measured wheel torque.','Steering units are the AC API output; .03 is a sampling filter, not a calibration.','No brake-balance or grass-grip pass is inferred from raw samples.']}
print(json.dumps(result,indent=2))
if a.out:a.out.write_text(json.dumps(result,indent=2))
