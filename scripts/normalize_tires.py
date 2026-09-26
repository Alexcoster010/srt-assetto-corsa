"""Normalize visual wheels to SRT 18x6-10 tire envelope; physics radius remains 0.2286 m."""
from pathlib import Path
import struct,json,argparse
import numpy as np

def normalize(path,report_path=None):
 path=Path(path);b=bytearray(path.read_bytes());o=6
 def rd(fmt):
  nonlocal o
  n=struct.calcsize('<'+fmt);v=struct.unpack_from('<'+fmt,b,o);o+=n;return v[0] if len(v)==1 else v
 def st():
  nonlocal o
  n=rd('i');s=b[o:o+n].decode();o+=n;return s
 v=rd('i')
 if v>5:rd('i')
 for _ in range(rd('i')):rd('i');st();n=rd('i');o+=n
 for _ in range(rd('i')):
  st();st();rd('BBi')
  for j in range(rd('i')):st();rd('10f')
  for j in range(rd('i')):st();rd('i');st()
 groups={};dummy={}
 def node(group=None):
  nonlocal o
  typ=rd('i');name=st();count=rd('i');rd('B')
  if typ==1:
   pos=o;rd('16f')
   if name.startswith('WHEEL_'):group=name;dummy[name]=pos
   if name.startswith('SUSP_'):dummy[name]=pos
  elif typ==2:
   rd('3B');nv=rd('i');start=o;o+=nv*44;ni=rd('i');o+=ni*2;tail=o;rd('II6fB')
   if group:groups.setdefault(group,[]).append((name,start,nv,tail))
  else:raise ValueError('Expected flattened r05 model')
  for _ in range(count):node(group)
 node();assert o==len(b)
 reports={}
 for name,ms in groups.items():
  tyre=next(m for m in ms if m[0].startswith('Tyre'));a=np.frombuffer(b,dtype='<f4',count=tyre[2]*11,offset=tyre[1]).reshape(-1,11).copy();lo=a[:,:3].min(0);hi=a[:,:3].max(0);center=(lo+hi)/2;scale=np.array([.1524,.4572,.4572])/(hi-lo)
  for mn,start,nv,tail in ms:
   v=np.frombuffer(b,dtype='<f4',count=nv*11,offset=start).reshape(-1,11).copy();v[:,:3]=(v[:,:3]-center)*scale;v[:,3:6]/=scale;v[:,3:6]/=np.maximum(np.linalg.norm(v[:,3:6],axis=1)[:,None],1e-12);b[start:start+nv*44]=v.astype('<f4').tobytes();c=v[:,:3].mean(0);radius=float(np.linalg.norm(v[:,:3]-c,axis=1).max());struct.pack_into('<4f',b,tail+16,*c,radius)
  code=name[-2:];p=[.57785 if code[0]=='L' else -.57785,.2286,1.07315 if code[1]=='F' else -.59055]
  for k in [name,'SUSP_'+code]:
   if k in dummy:struct.pack_into('<3f',b,dummy[k]+48,*p)
  reports[name]={'visual_width_m':.1524,'visual_OD_m':.4572,'visual_OD_in':18,'wheel_center_m':p,'scale_from_previous':scale.tolist()}
 path.write_bytes(b)
 if report_path:Path(report_path).write_text(json.dumps({'wheels':reports,'physics_radius_m':.2286,'nominal_rim_diameter_in':10,'note':'Visual tire/rim group normalized to 18x6 envelope. AC rim collision radius convention retained.'},indent=2))
 return reports
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('model');p.add_argument('--report');a=p.parse_args();print(json.dumps(normalize(a.model,a.report)))
