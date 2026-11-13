from pathlib import Path
import struct,zipfile,json,numpy as np
R=Path('engineering/srt-assetto-corsa/release-r17')
def parse(b):
 o=6; meshes=[];trans=[]
 def rd(fmt):
  nonlocal o
  n=struct.calcsize('<'+fmt);v=struct.unpack_from('<'+fmt,b,o);o+=n;return v[0] if len(v)==1 else v
 def ss():
  nonlocal o
  n=rd('i');s=b[o:o+n].decode();o+=n;return s
 ver=rd('i');assert ver in [5,6]
 if ver==6:rd('i')
 ntpos=o;nt=rd('i');textures=[]
 for _ in range(nt):rd('i');textures.append(ss());n=rd('i');o+=n
 matpos=o;nm=rd('i');mats=[]
 for _ in range(nm):
  name=ss();shader=ss();rd('BBi');props={}
  for _ in range(rd('i')):k=ss();props[k]=rd('10f')
  tx=[]
  for _ in range(rd('i')):name2=ss();rd('i');tx.append(ss())
  mats.append({'name':name,'shader':shader,'textures':tx})
 rootpos=o;rootchildren=None
 def node(parent=np.eye(4)):
  nonlocal o,rootchildren
  typ=rd('i');name=ss();cntpos=o;n=rd('i');rd('B');xf=parent
  if rootchildren is None:rootchildren=cntpos
  if typ==1:
   xf=np.array(rd('16f')).reshape(4,4)@parent;trans.append({'name':name,'transform':xf.tolist()})
  else:
   assert typ==2;rd('3B');nv=rd('i');v=np.frombuffer(b,dtype='<f4',count=nv*11,offset=o).reshape(nv,11).copy();o+=nv*44;ni=rd('i');idx=np.frombuffer(b,dtype='<u2',count=ni,offset=o).copy();o+=ni*2;tail=rd('II6fB');p=np.c_[v[:,:3],np.ones(nv)]@parent
   tri=p[idx.reshape(-1,3),:3];vol=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6)
   meshes.append({'name':name,'min':p[:,:3].min(0).tolist(),'max':p[:,:3].max(0).tolist(),'vertices':nv,'triangles':ni//3,'signed_volume':vol,'material':tail[0]})
  for _ in range(n):node(xf)
 node();assert o==len(b),(o,len(b))
 return {'version':ver,'meshes':meshes,'transforms':trans,'textures':textures,'materials':mats,'texture_count_offset':ntpos,'material_count_offset':matpos,'root_offset':rootpos,'root_children_offset':rootchildren,'texture_count':nt,'material_count':nm}
with zipfile.ZipFile(R/'baseline-r16.zip') as z:
 for filename in ['collider.kn5','srt27_prototype.kn5']:
  result=parse(z.read('content/cars/srt27_prototype/'+filename));(R/(filename+'.json')).write_text(json.dumps(result,indent=2));print(filename,json.dumps(result if filename=='collider.kn5' else {'mesh_count':len(result['meshes']),'rear_meshes':[m for m in result['meshes'] if any(s in m['name'].lower() for s in ['rear_wing','frame','tyre'])],'textures':result['textures'][:6]},indent=2))
 for f in ['car.ini','colliders.ini','lights.ini']:(R/('baseline-'+f)).write_bytes(z.read('content/cars/srt27_prototype/data/'+f))
