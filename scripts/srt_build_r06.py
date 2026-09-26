from pathlib import Path
import os,json,struct,io,shutil,configparser,hashlib,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(os.environ.get('SRT_AC_PROJECT',str(Path(__file__).resolve().parents[1])));BASE=Path(os.environ.get('SRT_BASE_CAR',str(P/'release-r05/content/cars/srt27_prototype')));R=P/'release-r06';R.mkdir(exist_ok=True);O=R/'content/cars/srt27_prototype';shutil.copytree(BASE,O,dirs_exist_ok=True)
C=P/'cad-r06';parts={c['source']:c for c in json.loads((C/'parts-visible/parts.json').read_text()) if 'file' in c and c['triangles']>0};components=json.loads((C/'master25/assembly.json').read_text())['components'];meshes=[];evidence=[];excluded=[]
textures=[];materials=[];colors={};helpers={};offset=np.array([0,0,-.090043])
def material(name,color,im=None):
 if im is None:im=Image.new('RGB',(4,4),color)
 f=io.BytesIO();im.save(f,format='DDS');textures.append((name+'.dds',f.getvalue()));materials.append(name);colors[len(materials)-1]=color;return len(materials)-1
white=material('SRT_WHITE',(235,236,238));carbon=material('SRT_CARBON',(25,27,29));metal=material('SRT_ALUMINUM',(150,154,160));rubber=material('SRT_RUBBER',(25,25,26));steel=material('SRT_FRAME',(28,29,31));gold=material('SRT_DAMPER',(163,121,47))
im=Image.new('RGB',(1024,1024),(28,29,31));d=ImageDraw.Draw(im)
for y in range(0,1024,8):
 for x in range(0,1024,8):
  shade=31 if (x//8+y//8)%2 else 23;d.rectangle((x,y,x+7,y+7),fill=(shade,shade+1,shade+2))
d.ellipse((310,675,714,890),fill=(241,242,242));font=ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf',205);d.text((512,780),'31',font=font,anchor='mm',fill=(20,21,23))
for x in range(-100,1100,135):d.polygon([(x,970),(x+52,970),(x+135,1023),(x+83,1023)],fill=(240,241,242))
nosemat=material('SRT_NOSE_31',(32,33,35),im)

def world(c):
 p=parts[c['source']];v=np.fromfile(C/'parts-visible'/p['file'],dtype='<f4').reshape(-1,3,3).astype(float);t=np.array(c['transform']);return (v@t[:9].reshape(3,3))*t[12]+t[9:12]+offset

def emit(name,tri,mat,group=None,smooth=False,uv=None):
 if len(tri)==0:return
 # Weld normals across coincident CAD tessellation vertices for curved tubes and tires.
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);valid=np.linalg.norm(normals,axis=1)>1e-11;tri=tri[valid];normals=normals[valid];normals/=np.linalg.norm(normals,axis=1)[:,None]
 if uv is not None:uv=uv[valid]
 for st in range(0,len(tri),18000):
  t=tri[st:st+18000];v=t.reshape(-1,3);n=np.repeat(normals[st:st+18000],3,axis=0)
  if smooth:
   _,inv=np.unique(np.round(v,6),axis=0,return_inverse=True);sums=np.zeros((inv.max()+1,3));np.add.at(sums,inv,n);sums/=np.maximum(np.linalg.norm(sums,axis=1)[:,None],1e-9);n=sums[inv]
  tx=np.zeros((len(v),2)) if uv is None else uv[st:st+18000].reshape(-1,2)
  a=np.c_[v,n,tx,np.tile([1,0,0],(len(v),1))];meshes.append(dict(name=re.sub('[^A-Za-z0-9_]+','_',name)[:140]+'_'+hashlib.sha1(name.encode()).hexdigest()[:10]+'_'+str(st),v=a,mat=mat,group=group))

# Use native team CAD; no MAD car-body, cockpit, or wheel meshes are used.
wheel_candidates=[]
for c in components:
 if c['source'] not in parts:continue
 name=c['name'];lower=name.lower();tri=world(c)
 if any(x in lower for x in ['shelfhalf','wheelcenter','tire_model']):wheel_candidates.append((c,tri));continue
 if any(x in lower for x in ['19 inch rcv axle','seat model - v2','nylockforpaddles','firewall-','exhaust flange']):excluded.append(name);continue
 mat=carbon;group=None;smooth=False
 if 'frame_as_surface' in lower:
  n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-9);center=tri.mean(1);tri=tri[(abs(n[:,0])>.6)&(center[:,1]<.55)&(center[:,2]<.94)];mat=white
 elif 'frame-9' in lower:mat=steel;smooth=True
 elif 'kawasaki' in lower or 'oil_pan' in lower or 'drexler' in lower or 'rcv axle' in lower:mat=metal;smooth=True
 elif 'linkage_tube' in lower or 'tie_rod' in lower or 'steering_column' in lower:mat=steel;smooth=True
 elif 'upright' in lower or 'bellcrank' in lower or 'firewall remake' in lower:mat=metal
 elif 'steeringwheel' in lower:
  group='STEER_HR';helpers[group]=np.array([0,.466725,.64849432]);mat=carbon if 'wheel-1' in lower else metal
 elif 'nose' in lower:
  normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-9);top=(abs(normals[:,1])>.40)&(tri[:,:,1].mean(1)>.30)
  # UV follows the physical X/Z coordinates; front of nose at high Z.
  uv=np.stack([(tri[:,:,0]+.246)/.492,(tri[:,:,2]-.888)/1.09],axis=2)
  emit('SRT_NATIVE_NOSE_WHITE',tri[~top],white,smooth=True);emit('SRT_NATIVE_NOSE_NUMBER31',tri[top],nosemat,smooth=True,uv=uv[top]);evidence.append({'name':name,'source':c['source'],'triangles':len(tri)});continue
 elif 'front wing' in lower or 'rear wing' in lower:
  # Keep native airfoil shape. White/silver edge treatment is inferred from the unveiling photo.
  y=tri[:,:,1].mean(1);x=abs(tri[:,:,0].mean(1));edge=(x>.608)|(tri[:,:,2].mean(1)>1.865) if 'front wing' in lower else (x>.475)|(y>1.13)
  emit('SRT_NATIVE_'+name+'_EDGE',tri[edge],white);emit('SRT_NATIVE_'+name,tri[~edge],carbon,smooth=True);evidence.append({'name':name,'source':c['source'],'triangles':len(tri)});continue
 elif 'undertray' in lower:mat=carbon
 elif 'seat' in lower or 'restraint' in lower:mat=rubber
 if np.max(np.abs(tri))>5:excluded.append(name+' invalid/outlying bounds');continue
 emit('SRT_NATIVE_'+name,tri,mat,group,smooth);
 if '17 inch rcv axle' in lower:
  mirrored=tri.copy();mirrored[:,:,0]*=-1;emit('SRT_NATIVE_MIRRORED_AXLE',mirrored[:,[0,2,1]],mat,smooth=True)
 evidence.append({'name':name,'source':c['source'],'triangles':len(tri)})

# Replicate the coherent right-front native rim assembly; some saved left rim instances are displaced.
canonical=[]
for c,t in wheel_candidates:
 center=(t.reshape(-1,3).min(0)+t.reshape(-1,3).max(0))/2
 if center[0]>.4 and center[2]>.8:canonical.append((c,t))
assert len(canonical)==4,[(x[0]['name']) for x in canonical]
for group,pivot in [('WHEEL_LF',[-.57785,.2286,1.07315]),('WHEEL_RF',[.57785,.2286,1.07315]),('WHEEL_LR',[-.57785,.2286,-.59055]),('WHEEL_RR',[.57785,.2286,-.59055])]:
 helpers[group]=np.array(pivot);helpers[group.replace('WHEEL','SUSP')]=np.array(pivot)
 for c,t in canonical:
  local=t-np.array([.6096,.2286,1.07315]);istire='tire_model' in c['name'].lower()
  if istire:
   mn=local.reshape(-1,3).min(0);mx=local.reshape(-1,3).max(0);local=(local-(mn+mx)/2)*np.array([.1524,.4572,.4572])/(mx-mn)
  if pivot[0]<0:local[:,:,0]*=-1;local=local[:,[0,2,1]]
  emit('SRT_Tyre_'+group if istire else 'SRT_Rim_'+c['name']+'_'+group,local+helpers[group],rubber if istire else metal,group,True)

# Photo-derived sidepod shells: native sidepod CAD was not found. Explicit approximation.
outline=np.array([[.30,.79],[.43,.82],[.58,.80],[.65,.68],[.65,.10],[.58,-.25],[.32,-.38],[.29,.20]])
curve=[]
for k in range(len(outline)):
 p0,p1,p2,p3=[outline[(k+j)%len(outline)] for j in [-1,0,1,2]]
 for u in np.linspace(0,1,8,endpoint=False):curve.append(.5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u*u*u))
curve=np.array(curve)
for sign in [-1,1]:
 top=np.c_[curve[:,0]*sign,.385+.015*curve[:,1],curve[:,1]];bottom=top.copy();bottom[:,1]=.15;center=top.mean(0);tt=[];side=[]
 for i in range(len(top)):
  j=(i+1)%len(top);tt.append([center,top[i],top[j]]);side.extend([[top[i],bottom[i],bottom[j]],[top[i],bottom[j],top[j]]])
 tt=np.array(tt);side=np.array(side)
 if sign<0:tt=tt[:,[0,2,1]];side=side[:,[0,2,1]]
 emit('SRT_PHOTO_SIDEPOD_TOP_'+str(sign),tt,white,smooth=True);emit('SRT_PHOTO_SIDEPOD_SIDES_'+str(sign),side,carbon,smooth=True)

# Binary KN5 with only original team meshes and original procedural materials.
buf=io.BytesIO()
def wr(f,*v):buf.write(struct.pack('<'+f,*v))
def ss(s):v=s.encode();wr('i',len(v));buf.write(v)
buf.write(b'sc6969');wr('i',5);wr('i',len(textures))
for name,data in textures:wr('i',1);ss(name);wr('i',len(data));buf.write(data)
wr('i',len(materials))
for name in materials:
 ss(name);ss('ksPerPixel');wr('BBi',0,0,0);wr('i',4)
 for k,v in [('ksAmbient',.45),('ksDiffuse',.65),('ksSpecular',.32),('ksSpecularEXP',35)]:ss(k);wr('10f',v,*([0]*9))
 wr('i',1);ss('txDiffuse');wr('i',0);ss(name+'.dds')
def base(name,n,p=(0,0,0)):
 wr('i',1);ss(name);wr('iB',n,1);wr('16f',1,0,0,0,0,1,0,0,0,0,1,0,*p,1)
def mesh(m,p=(0,0,0)):
 a=m['v'].copy();a[:,:3]-=p;wr('i',2);ss(m['name']);wr('i4Bi',0,1,1,1,0,len(a));buf.write(a.astype('<f4').tobytes());wr('i',len(a));buf.write(np.arange(len(a),dtype='<u2').tobytes());center=a[:,:3].mean(0);radius=np.linalg.norm(a[:,:3]-center,axis=1).max();wr('II6fB',m['mat'],0,0,2000,*center,radius,1)
solo=[m for m in meshes if m['group'] is None];groups={g:[m for m in meshes if m['group']==g] for g in helpers}
base('SRT_NATIVE_2025_2026',len(solo)+len(groups))
for m in solo:mesh(m)
for g,ms in groups.items():
 base(g,len(ms),helpers[g])
 for m in ms:mesh(m,helpers[g])
(O/'srt27_prototype.kn5').write_bytes(buf.getvalue())
# Store renderable geometry without rerunning CAD or the game build.
np.savez_compressed(R/'geometry.npz',**{str(i):m['v'] for i,m in enumerate(meshes)})
(R/'meshes.json').write_text(json.dumps([{'name':m['name'],'mat':m['mat'],'group':m['group'],'color':colors[m['mat']]} for m in meshes],indent=2))
proof={}
for n in ['engine.ini','power.lut','drivetrain.ini','suspensions.ini','tyres.ini','brakes.ini','aero.ini']:
 v=(O/'data'/n).read_bytes();assert v==(BASE/'data'/n).read_bytes();proof[n]=hashlib.sha256(v).hexdigest()
report={'revision':'r06','geometry':'native team SRT25 assembly parts, with original procedural livery; no donor vehicle meshes','components':evidence,'excluded':excluded,'mesh_count':len(meshes),'triangle_count':sum(len(m['v'])//3 for m in meshes),'bytes':len(buf.getvalue()),'physics_preserved':proof,'transform_note':'Native assembly X lateral,Y up,Z forward; translated -0.090043m Z to align front axle. Native frame shape unscaled. Wheels use active physics locations. Native saved rear axle differs by about18mm from selected physics wheelbase.','runtime_test':'pending','limits':['Sidepod shells are photo-derived approximations; native sidepod CAD was not located.','Native part selection and color zoning inferred from public 2026 unveiling photo; not an as-built survey.','Source assembly contains suppressed design alternatives. Original file states preserved.','Visual suspension linkages remain static. Driver animation and engine audio remain local temporary assets.']}
(R/'build-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['revision','mesh_count','triangle_count','bytes']}))


