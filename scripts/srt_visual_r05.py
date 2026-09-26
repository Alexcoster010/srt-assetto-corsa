from pathlib import Path
import struct,json,os,io,math,shutil,hashlib,configparser
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(os.environ['SRT_AC_PROJECT']); T=Path(os.environ['TEMP']); donor=Path(os.environ['MAD_MFT02_DIR']); R=P/'release-r05'; out=R/'content/cars/srt27_prototype';out.mkdir(parents=True,exist_ok=True)
shutil.copytree(P/'release-r03/content/cars/srt27_prototype',out,dirs_exist_ok=True)
b=(donor/'madformulateam_mft02.kn5').read_bytes();o=6

def rd(fmt):
 global o
 n=struct.calcsize('<'+fmt);v=struct.unpack_from('<'+fmt,b,o);o+=n;return v[0] if len(v)==1 else v

def st():
 global o
 n=rd('i');s=b[o:o+n].decode();o+=n;return s
ver=rd('i')
if ver>5:rd('i')
textures=[]
for _ in range(rd('i')):
 active=rd('i');name=st();n=rd('i');textures.append((active,name,b[o:o+n]));o+=n
mats=[]
for _ in range(rd('i')):
 name=st();shader=st();blend,alpha,depth=rd('BBi');props=[(st(),rd('10f')) for j in range(rd('i'))];maps=[(st(),rd('i'),st()) for j in range(rd('i'))];mats.append((name,shader,blend,alpha,depth,props,maps))
meshes=[];helpers={};nodes=0
xf=np.diag([1.1557/1.17,.2286/.232,1.6637/1.545,1.]);xf[3,2]=1.07315-.5199318*xf[2,2]
# Full row-vector world transforms; preserve each wheel's circular geometry while moving its center.
def parse(parent=np.eye(4),group=None,anc=()):
 global o,nodes
 typ=rd('i');name=st();children=rd('i');active=rd('B');nodes+=1;world=parent
 if typ==1:
  world=np.array(rd('16f')).reshape(4,4)@parent
  if name in ['WHEEL_LF','WHEEL_RF','WHEEL_LR','WHEEL_RR','SUSP_LF','SUSP_RF','SUSP_LR','SUSP_RR','STEER_HR']:
   group=name;helpers[name]=world[3,:]@xf
 elif typ in (2,3):
  flags=rd('3B')
  if typ==3:
   for _ in range(rd('i')):st();rd('16f')
  nv=rd('i');v=[]
  for _ in range(nv):
   v.append(rd('11f'))
   if typ==3:rd('8f')
  ni=rd('i');inds=rd(str(ni)+'H') if ni else ();mat,layer=rd('II');tail=rd('6fB') if typ==2 else None
  if typ==3:o+=8
  a=np.array(v,dtype=float)
  if nv:
   pos=np.c_[a[:,:3],np.ones(nv)]@parent
   if group and group.startswith(('WHEEL_','SUSP_')):
    origin=helpers[group][:3]; oldorigin=np.r_[origin,1.]@np.linalg.inv(xf);pos[:,:3]=(pos[:,:3]-oldorigin[:3])*(.2286/.232)+origin
   else:pos=pos@xf
   normal=a[:,3:6]@np.linalg.inv((parent@xf)[:3,:3]).T;normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12)
   tangent=a[:,8:11]@(parent@xf)[:3,:3];tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-12)
   a[:,:3]=pos[:,:3];a[:,3:6]=normal;a[:,8:11]=tangent
   meshes.append(dict(name=name,group=group,anc=anc,vertices=a,indices=list(inds) if ni>1 else [inds],mat=mat,flags=flags,active=active,skinned=typ==3))
 else:raise ValueError(typ)
 for _ in range(children):parse(world,group,anc+(name,))
parse();assert o==len(b)
# Original procedural materials and small race-number graphic; donor texture bytes remain untouched.
def material(name,color,graphic=False):
 im=Image.new('RGB',(512,512) if graphic else (4,4),color)
 if graphic:
  d=ImageDraw.Draw(im);d.ellipse((8,8,504,504),fill='white');font=ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf',300);d.text((256,248),'31',font=font,anchor='mm',fill=(12,12,14))
 mem=io.BytesIO();im.save(mem,format='DDS');tex=name+'.dds';textures.append((1,tex,mem.getvalue()));idx=len(mats);mats.append((name,'ksPerPixel',0,0,0,[(k,(v,0,0,0,0,0,0,0,0,0)) for k,v in [('ksAmbient',.45),('ksDiffuse',.65),('ksSpecular',.25),('ksSpecularEXP',35)]],[('txDiffuse',0,tex)]));return idx
white=material('SRT_WHITE',(237,239,239));black=material('SRT_BLACK',(20,22,25));number=material('SRT_NUMBER_31',(20,22,25),True)
removed=[]
kept=[]
for m in meshes:
 n=m['name'].lower()
 if n in ['nosecone','nosewings'] or n.startswith(('fw','rw')) or 'blur' in n or 'STEER_LR' in m['anc']:
  removed.append(m['name']);continue
 if n in ['monocoque','monocoquecf']:
  m['mat']=white
  tri=np.array(m['indices']).reshape(-1,3);keep=m['vertices'][tri,2].mean(axis=1)<.90;m['indices']=tri[keep].reshape(-1).tolist()
  if not m['indices']:continue
 if n.startswith(('fw','rw')) or n in ['floorcover','diffuser_body']:m['mat']=black
 kept.append(m)
meshes=kept
# Actual SRT25/26 nose and wing tessellation, in native meters, placed using saved CFD assembly transforms.
cad=P/'cad-r05'
assembly=json.loads((cad/'srt-2026-cfd-flat.json').read_text(encoding='utf-8-sig'));parts=json.loads(assembly['cadState']['features'][0])['components']
# CFD assembly X points rearward, Y lateral, Z up. Preserve CAD shape; align its front axle to current SRT physics.
for slug,needle in [('nose','Nose 25-1'),('front-wing','SRT25 Front Wing Final CFD-1'),('rear-wing','SRT25 rear Wing Final CFD-1')]:
 c=next(c for c in parts if c['name']==needle);tr=np.array(c['transform']);rot=tr[:9].reshape(3,3);xyz=tr[9:12];tri=np.fromfile(cad/(slug+'-native-triangles.bin'),dtype='<f4').reshape(-1,3,3)
 pp=tri@rot+xyz;ac=np.stack([-pp[:,:,1],pp[:,:,2],-pp[:,:,0]-.09017],axis=2)
 normals=np.cross(ac[:,1]-ac[:,0],ac[:,2]-ac[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
 # Split nose upper carbon and lower white using geometric surface orientation; no change to CAD vertices.
 carbon=(normals[:,1]>.40)&(ac[:,:,1].mean(axis=1)>.30) if slug=='nose' else np.ones(len(ac),dtype=bool)
 for is_black in [False,True]:
  subset=ac[carbon==is_black];nn=normals[carbon==is_black]
  for start in range(0,len(subset),20000):
   vv=subset[start:start+20000].reshape(-1,3);nv=len(vv)
   if not nv:continue
   norms=np.repeat(nn[start:start+20000],3,axis=0);v=np.c_[vv,norms,np.zeros((nv,2)),np.tile([1,0,0],(nv,1))]
   meshes.append(dict(name='SRT_CAD_'+slug+('_CARBON' if is_black else '_WHITE')+'_'+str(start),group=None,anc=(),vertices=v,indices=list(range(nv)),mat=black if is_black else white,flags=(1,1,0),active=1,skinned=False))
# Native KN5 writer, preserves original texture/material definitions.
buf=io.BytesIO()
def wr(fmt,*args):buf.write(struct.pack('<'+fmt,*args))
def ss(v):v=v.encode();wr('i',len(v));buf.write(v)
buf.write(b'sc6969');wr('i',5);wr('i',len(textures))
for active,name,data in textures:wr('i',active);ss(name);wr('i',len(data));buf.write(data)
wr('i',len(mats))
for name,shader,blend,alpha,depth,props,maps in mats:
 ss(name);ss(shader);wr('BBi',blend,alpha,depth);wr('i',len(props))
 for key,val in props:ss(key);wr('10f',*val)
 wr('i',len(maps))
 for key,slot,tex in maps:ss(key);wr('i',slot);ss(tex)
def base(name,count,p=(0,0,0)):
 wr('i',1);ss(name);wr('iB',count,1);wr('16f',1,0,0,0,0,1,0,0,0,0,1,0,*p,1)
def emit(m,p=(0,0,0)):
 a=m['vertices'].copy();a[:,:3]-=np.array(p);wr('i',2);ss(m['name']);wr('i4Bi',0,m['active'],*m['flags'],len(a));buf.write(a.astype('<f4').tobytes());wr('i',len(m['indices']));buf.write(np.array(m['indices'],dtype='<u2').tobytes());center=a[:,:3].mean(axis=0);radius=np.linalg.norm(a[:,:3]-center,axis=1).max();wr('II6fB',m['mat'],0,0,2000,*center,radius,1)
groups={};solo=[]
for m in meshes:
 if m['group']:groups.setdefault(m['group'],[]).append(m)
 else:solo.append(m)
base('SRT_MAD_TEMP_VISUAL',len(solo)+len(groups))
for m in solo:emit(m)
for name,ms in groups.items():
 p=helpers[name][:3];base(name,len(ms),p)
 for m in ms:emit(m,p)
(out/'srt27_prototype.kn5').write_bytes(buf.getvalue())
from normalize_tires import normalize
normalize(out/'srt27_prototype.kn5',R/'tire-dimension-check.json')
# Adapt visual-only settings; preserve physical parameters and data files.
for n in ['animations','texture']:shutil.copytree(donor/n,out/n,dirs_exist_ok=True)
shutil.copy2(donor/'driver_base_pos.knh',out/'driver_base_pos.knh')
shutil.copytree(donor/'skins/2022_base',out/'skins/01_srt_white_black',dirs_exist_ok=True)
(out/'skins/01_srt_white_black/ui_skin.json').write_text(json.dumps({'skinname':'SRT 2025-2026 white-black approximation','drivername':'Sooner Racing','country':'USA','number':'31'}))
# Clear donor preview to avoid presenting it as a render of our modified geometry.
(out/'skins/01_srt_white_black/preview.jpg').unlink(missing_ok=True)
def edit(name,sections):
 f=out/'data'/name;c=configparser.ConfigParser(strict=False,inline_comment_prefixes=(';',));c.optionxform=str;c.read(f)
 for s,values in sections.items():
  if not c.has_section(s):c.add_section(s)
  c[s].update({k:str(v) for k,v in values.items()})
 with f.open('w') as h:c.write(h,space_around_delimiters=False)
edit('car.ini',{'INFO':{'SCREEN_NAME':'Sooner Racing SRT27 - 2025/26 temporary visuals'},'BASIC':{'GRAPHICS_OFFSET':'0,-0.3,-0.208026'},'GRAPHICS':{'DRIVEREYES':'0,0.75,-0.08','ON_BOARD_PITCH_ANGLE':0,'USE_ANIMATED_SUSPENSIONS':0}})
edit('dash_cam.ini',{'DASH_CAM':{'POS':'0,0.70,0.10'}})
# Driver pose remains donor-sized: locate it with the same donor-to-SRT shift; animation is provisional.
edit('driver3d.ini',{'MODEL':{'POSITION':'0,0,0.513','NAME':'driver'},'STEER_ANIMATION':{'LOCK':100}})
ui=json.loads((out/'ui/ui_car.json').read_text());ui.update(name='Sooner Racing SRT27 - 2025/26 visuals',version='0.5',description='SRT physics with a private temporary MAD MFT02 visual adaptation. Actual SRT25/26 nose and wing CAD tessellation, positioned from saved assembly transforms; remaining detail temporarily from MAD. Donor detail retained. Shape, skin, driver pose and animation are provisional.');(out/'ui/ui_car.json').write_text(json.dumps(ui,indent=2))
proof={}
for n in ['engine.ini','power.lut','drivetrain.ini','suspensions.ini','tyres.ini','brakes.ini','aero.ini']:
 old=(P/'release-r03/content/cars/srt27_prototype/data'/n).read_bytes();new=(out/'data'/n).read_bytes();assert old==new;proof[n]=hashlib.sha256(new).hexdigest()
# Reference photos remain local; their public source is recorded in the build report.
report={'revision':'r05','reference':'https://www.linkedin.com/company/sooner-racing-team','reference_car':'2025-2026 white/black; actual Nose25 and SRT25 final CFD wing CAD with assembly placement','donor':'standard IC madformulateam_mft02 from user downloaded v1.42 archive','donor_nodes_read':nodes,'meshes_written':len(meshes),'removed_donor_meshes':removed,'donor_world_to_srt_visual':xf.tolist(),'physics_sha256_unchanged':proof,'limits':['Nose and wings from native SRT CAD; retained MAD body and cockpit are temporary. SRT25 wings were suppressed in CFD study: chosen using supplied year and photo silhouette; as-built verification pending.','driver pose, visual suspension and moving details require visual validation','single visual LOD temporary','no public redistribution; preserve MAD attribution'],'game_test':'pending'}
(R/'visual-build-report.json').write_text(json.dumps(report,indent=2));(out/'LOCAL_ASSET_PROVENANCE.txt').write_text('Private local prototype. MAD Formula Team MFT02 visuals by Ofitus21/MAD Formula Team, user-supplied official archive. Original MAD archive preserved. SRT photo-inspired nose/sidepod approximation, not exact CAD. Kunos temporary Tatuus audio. No distribution package authorized.\n')
# Save geometry for an independent overview renderer.
np.savez_compressed(R/'visual-review.npz',**{str(i):m['vertices'][:,:3] for i,m in enumerate(meshes)})
print(json.dumps({'output':str(out),'meshes':len(meshes),'physics_files_preserved':len(proof)}))

