from pathlib import Path
import struct,json,numpy as np,hashlib,os
P=Path(os.environ.get('SRT_AC_PROJECT',str(Path(__file__).resolve().parents[1])));f=P/'release-r07/content/cars/srt27_prototype/srt27_prototype.kn5';b=f.read_bytes();o=6;names=[];bounds={}
def rd(fmt):
 global o
 n=struct.calcsize('<'+fmt);v=struct.unpack_from('<'+fmt,b,o);o+=n;return v[0] if len(v)==1 else v
def ss():
 global o
 n=rd('i');s=b[o:o+n].decode();o+=n;return s
assert b[:6]==b'sc6969' and rd('i')==5
for _ in range(rd('i')):rd('i');ss();n=rd('i');o+=n
for _ in range(rd('i')):
 ss();ss();rd('BBi')
 for j in range(rd('i')):ss();rd('10f')
 for j in range(rd('i')):ss();rd('i');ss()
def node(parent=np.eye(4),group=None):
 global o
 typ=rd('i');name=ss();names.append(name);n=rd('i');rd('B');xf=parent
 if typ==1:
  xf=np.array(rd('16f')).reshape(4,4)@parent
  if name.startswith('WHEEL_'):group=name
 else:
  assert typ==2;rd('3B');nv=rd('i');v=np.frombuffer(b,dtype='<f4',count=nv*11,offset=o).reshape(nv,11);o+=nv*44;ni=rd('i');idx=np.frombuffer(b,dtype='<u2',count=ni,offset=o);assert idx.max()<nv;o+=ni*2;rd('II6fB');assert np.isfinite(v).all()
  if 'SRT_Tyre' in name:
   p=np.c_[v[:,:3],np.ones(nv)]@parent;bounds[group]={'center_m':((p[:,:3].min(0)+p[:,:3].max(0))/2).tolist(),'dimensions_m':np.ptp(p[:,:3],axis=0).tolist()}
 for _ in range(n):node(xf,group)
node();assert o==len(b);assert len(names)==len(set(names)),[n for n in names if names.count(n)>1]
for d in bounds.values():assert np.allclose(d['dimensions_m'],[.1524,.4572,.4572],atol=1e-6)
result={'exact_eof':True,'nodes':len(names),'unique_node_names':True,'binary_tire_readback':bounds,'sha256':hashlib.sha256(b).hexdigest()};(P/'release-r07/kn5-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
