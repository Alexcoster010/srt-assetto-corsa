from pathlib import Path
import struct,json,numpy as np,hashlib,configparser,os
P=Path(os.environ.get('SRT_TRACK_PROJECT',str(Path(__file__).resolve().parents[1])));R=P/'release-r01';T=R/'content/tracks/srt_michigan_autocross';b=(T/'srt_michigan_autocross.kn5').read_bytes();o=6;names=[];helper={};physical={};verts=[]
def rd(fmt):
 global o
 n=struct.calcsize('<'+fmt);v=struct.unpack_from('<'+fmt,b,o);o+=n;return v[0] if len(v)==1 else v
def ss():
 global o
 n=rd('i');s=b[o:o+n].decode();o+=n;return s
assert b[:6]==b'sc6969' and rd('i')==5
for _ in range(rd('i')):rd('i');ss();n=rd('i');o+=n
nm=rd('i')
for _ in range(nm):
 ss();ss();rd('BBi')
 for j in range(rd('i')):ss();rd('10f')
 for j in range(rd('i')):ss();rd('i');ss()
def node():
 global o
 typ=rd('i');name=ss();names.append(name);nc=rd('i');rd('B')
 if typ==1:
  xf=np.array(rd('16f')).reshape(4,4)
  if name.startswith('AC_'):helper[name]=xf
 else:
  assert typ==2 and nc==0;rd('3B');n=rd('i');v=np.frombuffer(b,dtype='<f4',count=n*11,offset=o).reshape(n,11);o+=n*44;ni=rd('i');idx=np.frombuffer(b,dtype='<u2',count=ni,offset=o);o+=ni*2;mat=rd('II6fB')[0];assert idx.max()<n and mat<nm and np.isfinite(v).all();verts.append(v[:,:3])
  if name[0].isdigit():
   assert name.startswith(('1ASPHALT','1GRASS'));assert np.allclose(v[:,1],0);assert np.all(v[:,4]>.99);physical[name]={'triangles':ni//3,'normal_up':True}
 for _ in range(nc):node()
node();assert o==len(b) and len(names)==len(set(names));assert all(n in helper for n in ['AC_PIT_0','AC_START_0','AC_HOTLAP_START_0']+[f'AC_TIME_{i}_{s}' for i in range(3) for s in ['L','R']])
for x in helper.values():assert np.isclose(np.linalg.det(x[:3,:3]),1)
C=json.loads((P/'reference-copies/course-r25b.json').read_text());E=json.loads((R/'course-export.json').read_text());path=np.array(E['path_ac_m']);native=np.array(C['driving_path_xz_m']);assert np.allclose(path[:len(native),[2,0]]*np.array([1,-1]),native,atol=1e-12);assert np.array_equal(path[0],path[-1]);coneerr=[]
for c,d in zip(C['cones'],E['cones']):
 exp=np.array([-c['position_xz_m'][1],0,c['position_xz_m'][0]]);coneerr.append(np.linalg.norm(exp-d['ac_position_m']));assert c['id']==d['id'] and c['role']==d['role']
 assert d['bounds_m'][0][1]>-.00001
assert max(coneerr)<1e-12
ai=(T/'ai/fast_lane.ai').read_bytes();ver,n,_,_=struct.unpack_from('<4i',ai);off=16;pts=np.array([struct.unpack_from('<4fi',ai,off+i*20)[:4] for i in range(n)]);off+=n*20;nx=struct.unpack_from('<i',ai,off)[0];off+=4;ex=np.frombuffer(ai,dtype='<f4',count=nx*18,offset=off).reshape(nx,18);off+=nx*72;grid=struct.unpack_from('<i',ai,off)[0];assert off+4==len(ai) and n==nx and ver==7 and grid==0;assert np.isfinite(ex).all() and np.all(np.diff(pts[:,3])>0);assert np.linalg.norm(pts[-1,:3]-pts[0,:3])<.3
result={'kn5_exact_eof':True,'unique_nodes':True,'model_sha256':hashlib.sha256(b).hexdigest(),'physics_meshes':physical,'helpers':len(helper),'source_cones':len(C['cones']),'maximum_cone_coordinate_error_m':max(coneerr),'original_path_round_trip':True,'closed_route_exact':True,'AI_points':n,'AI_exact_eof':True,'limits':'Static checks only; no driving, lap crossing or cone-penalty validation.'};(R/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
