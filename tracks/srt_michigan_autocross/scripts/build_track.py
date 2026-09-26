from pathlib import Path
import os,json,struct,io,math,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(os.environ.get('SRT_TRACK_PROJECT',str(Path(__file__).resolve().parents[1])));R=P/'release-r01';T=R/'content/tracks/srt_michigan_autocross';D=T/'data'
for folder in [D,T/'ai',T/'ui',P/'reference-copies',P/'scripts']:folder.mkdir(parents=True,exist_ok=True)
S=P/'reference-copies';source=S/'course-r25b.json';raw=source.read_bytes();C=json.loads(raw)
assert len(C['cones'])==137
for f in [source,S/'srt27_closed_course_connector_r26.m',S/'srt27_human_course_r26.m',S/'closed-course-validation.json']:
 dst=P/'reference-copies'/f.name
 if dst.exists():assert dst.read_bytes()==f.read_bytes(),str(dst)
 else:shutil.copy2(f,dst)
native=np.array(C['driving_path_xz_m']);q=native*np.array([1,-1]);start=q[0];finish=q[-1]
unit=lambda a:a/np.linalg.norm(a)
u=unit(q[1]-q[0]);v=unit(q[-1]-q[-2]);left=np.array([-u[1],u[0]]);approach=start-20*u;center=approach-30*left;entry=center-30*left
control=np.array([finish,finish+25*v,entry-26.1*v,entry]);n=int(np.ceil(np.linalg.norm(np.diff(control,axis=0),axis=1).sum()/.15))+1;t=np.linspace(0,1,n)[:,None]
A=(1-t)**3*control[0]+3*(1-t)**2*t*control[1]+3*(1-t)*t*t*control[2]+t**3*control[3]
th=np.linspace(-np.pi/2,-3*np.pi/2,int(np.ceil(np.pi*30/.15))+1);B=center+30*(np.cos(th)[:,None]*u+np.sin(th)[:,None]*left)
w=np.linspace(0,1,int(np.ceil(20/.15))+1)[:,None];E=approach+(start-approach)*w
ret=np.concatenate([A,B[1:],E[1:]]);ret[0]=finish;ret[-1]=start;closed=np.concatenate([q,ret[1:]])
# Proper rotation native [X,Y,Z] -> AC [-Z,Y,X]. Reduced path [X,-Z] -> AC [Y,0,X].
path=np.c_[closed[:,1],np.zeros(len(closed)),closed[:,0]];station=np.r_[0,np.cumsum(np.linalg.norm(np.diff(path,axis=0),axis=1))]
orig_s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(native,axis=0),axis=1))]
expected=json.loads((P/'reference-copies/closed-course-validation.json').read_text());assert len(path)==expected['closed_point_count'];assert abs(station[-1]-expected['closed_length_m'])<1e-7
cone_pos=np.array([[-c['position_xz_m'][1],0,c['position_xz_m'][0]] for c in C['cones']])
lo=np.minimum(path.min(0),cone_pos.min(0))-[20,0,20];hi=np.maximum(path.max(0),cone_pos.max(0))+[20,0,20]
meshes=[];helpers=[];mats=[];textures=[];rng=np.random.default_rng(31)
def material(name,color,noise=False):
 a=np.full((128,128,3),color,dtype=float)
 if noise:a+=rng.normal(0,3,(128,128,1))
 im=Image.fromarray(np.clip(a,0,255).astype('uint8'));buf=io.BytesIO();im.save(buf,format='DDS');textures.append((name+'.dds',buf.getvalue()));mats.append(name);return len(mats)-1
asphalt=material('SRT_Asphalt',(73,75,77),True);grass=material('SRT_Grass',(73,93,52),True);orange=material('SRT_ConeOrange',(241,92,20));white=material('SRT_White',(235,237,234));black=material('SRT_Rubber',(29,30,30));cyan=material('SRT_ReturnGuide',(51,181,194))
def emit(name,tri,mat,collide=False):
 tri=np.array(tri,dtype=float);norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);keep=np.linalg.norm(norm,axis=1)>1e-10;tri=tri[keep];norm=norm[keep];norm/=np.linalg.norm(norm,axis=1)[:,None]
 for i in range(0,len(tri),18000):
  p=tri[i:i+18000].reshape(-1,3);n=np.repeat(norm[i:i+18000],3,axis=0);uv=p[:,[0,2]]/5;a=np.c_[p,n,uv,np.tile([1,0,0],(len(p),1))];meshes.append(dict(name=name+('_'+str(i) if i else ''),a=a,mat=mat,collide=collide))
def plane(name,x0,x1,z0,z1,y,mat,physical=False):
 emit(name,[[[x0,y,z0],[x0,y,z1],[x1,y,z1]],[[x0,y,z0],[x1,y,z1],[x1,y,z0]]],mat,physical)
# Tile a continuous open lot. Paint and cone passage never turn asphalt into grass.
xs=np.linspace(lo[0],hi[0],int(np.ceil((hi[0]-lo[0])/15))+1);zs=np.linspace(lo[2],hi[2],int(np.ceil((hi[2]-lo[2])/15))+1)
for i in range(len(xs)-1):
 for j in range(len(zs)-1):plane('1ASPHALT_%d_%d'%(i,j),xs[i],xs[i+1],zs[j],zs[j+1],0,asphalt,True)
for i,box in enumerate([(lo[0]-80,lo[0],lo[2]-80,hi[2]+80),(hi[0],hi[0]+80,lo[2]-80,hi[2]+80),(lo[0],hi[0],lo[2]-80,lo[2]),(lo[0],hi[0],hi[2],hi[2]+80)]):plane('1GRASS_'+str(i),*box,0,grass,True)
# Original cone meshes; preserve upright/fallen role, height, base width and pointer heading.
def cube(h):
 vv=np.array([[x,y,z] for x in [-h,h] for y in [0,.035] for z in [-h,h]])
 faces=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]
 return np.array([[vv[f[0]],vv[f[1]],vv[f[2]]] for f in faces]+[[vv[f[0]],vv[f[2]],vv[f[3]]] for f in faces])
cone_bounds=[]
for idx,c in enumerate(C['cones']):
 h=float(c['height_m']);bw=float(c['base_width_m']);angle=float(c['tip_heading_rad']);pos=cone_pos[idx];up=np.array([0.,1.,0.]);forward=np.array([-np.sin(angle),0.,np.cos(angle)])
 if c['role']=='upright':
  bodybase=pos+up*.02;tip=pos+up*h;axes=np.eye(3);basecenter=pos+up*.01;dims=np.array([bw,.02,bw])
 else:
  bodybase=pos+up*bw/2;tip=pos+forward*np.sqrt(h*h-bw*bw/4);axes=np.array([forward,up,np.cross(forward,up)]).T;basecenter=bodybase;dims=np.array([.02,bw,bw])
 vv=np.array([[x,y,z] for x in [-1,1] for y in [-1,1] for z in [-1,1]])*dims/2;vv=vv@axes.T+basecenter
 faces=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]
 base=np.array([[vv[f[0]],vv[f[1]],vv[f[2]]] for f in faces]+[[vv[f[0]],vv[f[2]],vv[f[3]]] for f in faces]);emit('SRT_CONE_%03d_Base'%idx,base,black);transformed=[base]
 axis=unit(tip-bodybase);ref=np.array([0.,1.,0.]) if abs(axis[1])<.9 else np.array([1.,0.,0.]);uu=unit(np.cross(ref,axis));vvv=np.cross(axis,uu);fractions=[0,.50,.67,.82,1]
 for k in range(4):
  tri=[];f0=fractions[k];f1=fractions[k+1]
  for j in range(24):
   a=j*2*np.pi/24;b=(j+1)*2*np.pi/24;ra=np.cos(a)*uu+np.sin(a)*vvv;rb=np.cos(b)*uu+np.sin(b)*vvv
   v0=bodybase+(tip-bodybase)*f0+.30*bw*(1-f0)*ra;v1=bodybase+(tip-bodybase)*f0+.30*bw*(1-f0)*rb;v2=bodybase+(tip-bodybase)*f1+.30*bw*(1-f1)*rb;v3=bodybase+(tip-bodybase)*f1+.30*bw*(1-f1)*ra;tri.extend([[v0,v1,v2],[v0,v2,v3]])
  tri=np.array(tri);emit('SRT_CONE_%03d_Band%d'%(idx,k),tri,white if k==1 else orange);transformed.append(tri)
 vtx=np.concatenate(transformed).reshape(-1,3);cone_bounds.append({'id':c['id'],'role':c['role'],'source_position_xz_m':c['position_xz_m'],'ac_position_m':pos.tolist(),'tip_ac_m':tip.tolist(),'bounds_m':[vtx.min(0).tolist(),vtx.max(0).tolist()]})
# 4 m wide visual guide, as in the MATLAB renderer. It is not a legal or collision boundary.
def ribbon(points,offset,width,mat,name):
 tang=np.gradient(points,axis=0);norm=np.c_[tang[:,2],np.zeros(len(points)),-tang[:,0]];norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-9);a=points+norm*(offset-width/2);b=points+norm*(offset+width/2);a[:,1]=b[:,1]=.003;tri=[]
 for i in range(len(points)-1):tri.extend([[a[i],b[i+1],b[i]],[a[i],a[i+1],b[i+1]]])
 emit(name,tri,mat)
for side in [-1,1]:ribbon(path[:len(q)],side*2,.12,white,'SRT_EVENT_GUIDE_'+str(side));ribbon(path[len(q)-1:],side*2,.12,cyan,'SRT_SYNTHETIC_RETURN_'+str(side))
def at(s):
 i=min(np.searchsorted(station,s,side='right')-1,len(path)-2);f=(s-station[i])/(station[i+1]-station[i]);return path[i]*(1-f)+path[i+1]*f,unit(path[i+1]-path[i])
def helper(name,p,fwd):
 right=np.cross([0,1,0],fwd);xf=np.eye(4);xf[:3,:3]=[right,[0,1,0],fwd];xf[3,:3]=p;helpers.append((name,xf))
for name,s in [('AC_PIT_0',0),('AC_START_0',2),('AC_HOTLAP_START_0',0)]:
 p,f=at(s);p[1]=.25;helper(name,p,f)
timing=[float(C['timing_s_m'][0]),float(C['timing_s_m'][1]),orig_s[-1]+(station[-1]-orig_s[-1])*.5]
for i,s in enumerate(timing):
 p,f=at(s);left=np.array([f[2],0,-f[0]])
 for label,sign in [('L',1),('R',-1)]:helper('AC_TIME_%d_%s'%(i,label),p+left*sign*3.5,f)
 # Flat painted timing stripe.
 v=[p+left*3.5+f*.06,p-left*3.5+f*.06,p-left*3.5-f*.06,p+left*3.5-f*.06];v=np.array(v);v[:,1]=.004;emit('SRT_TIMING_PAINT_'+str(i),[v[[0,1,2]],v[[0,2,3]]],white if i<2 else cyan)
# Batch meshes by material/surface for efficient draw calls; retain per-cone positions in evidence.
old=meshes;meshes=[]
for mat in range(len(mats)):
 for physical in [False,True]:
  chunks=[m['a'][:,:3].reshape(-1,3,3) for m in old if m['mat']==mat and m['collide']==physical]
  if chunks:emit(('1ASPHALT' if mat==asphalt else '1GRASS') if physical else 'SRT_VISUAL_'+str(mat),np.concatenate(chunks),mat,physical)
# Native KN5 v5; only original textures and meshes.
buf=io.BytesIO()
def wr(fmt,*v):buf.write(struct.pack('<'+fmt,*v))
def ss(s):b=s.encode();wr('i',len(b));buf.write(b)
buf.write(b'sc6969');wr('i',5);wr('i',len(textures))
for name,data in textures:wr('i',1);ss(name);wr('i',len(data));buf.write(data)
wr('i',len(mats))
for name in mats:
 ss(name);ss('ksPerPixel');wr('BBi',0,0,0);wr('i',4)
 for k,v in [('ksAmbient',.4),('ksDiffuse',.6),('ksSpecular',.04),('ksSpecularEXP',12)]:ss(k);wr('10f',v,*([0]*9))
 wr('i',1);ss('txDiffuse');wr('i',0);ss(name+'.dds')
def base(name,n,xf):wr('i',1);ss(name);wr('iB',n,1);wr('16f',*xf.flatten())
base('SRT_AUTOCROSS_ROOT',len(meshes)+len(helpers),np.eye(4))
for m in meshes:
 a=m['a'];wr('i',2);ss(m['name']);wr('i4Bi',0,1,1,1,0,len(a));buf.write(a.astype('<f4').tobytes());wr('i',len(a));buf.write(np.arange(len(a),dtype='<u2').tobytes());center=a[:,:3].mean(0);radius=np.linalg.norm(a[:,:3]-center,axis=1).max();wr('II6fB',m['mat'],0,0,5000,*center,radius,1)
for name,xf in helpers:base(name,0,xf)
(T/'srt_michigan_autocross.kn5').write_bytes(buf.getvalue());(T/'models.ini').write_text('[MODEL_0]\nFILE=srt_michigan_autocross.kn5\nPOSITION=0,0,0\nROTATION=0,0,0\n')
# v7 AI spline layout from AcTools; retain all centerline points, omit duplicate terminal point.
# Rotate the spline origin to the original autocross timing start.
idx=int(np.argmin(abs(station-timing[0])));line=np.roll(path[:-1],-idx,axis=0);seg=np.linalg.norm(np.roll(line,-1,axis=0)-line,axis=1);dist=np.r_[0,np.cumsum(seg[:-1])];tangent=np.roll(line,-1,axis=0)-line;tangent/=np.linalg.norm(tangent,axis=1)[:,None]
f=io.BytesIO();f.write(struct.pack('<4i',7,len(line),0,0))
for i,p in enumerate(line):f.write(struct.pack('<4fi',p[0],.02,p[2],dist[i],i))
f.write(struct.pack('<i',len(line)))
for i in range(len(line)):f.write(struct.pack('<18f',30,.35,0,0,0,2,2,0,0,0,1,0,seg[i],*tangent[i],0,0))
f.write(struct.pack('<i',0));(T/'ai/fast_lane.ai').write_bytes(f.getvalue());(D/'ideal_line.ai').write_bytes(f.getvalue())
# Single-car practice circuit: no opponent AI or pit routing is claimed.
surf=''
for i,(key,fric,valid,dirt,vib) in enumerate([('ASPHALT',.98,1,0,0),('GRASS',.60,0,1,.2)]):
 surf+=f'[SURFACE_{i}]\nKEY={key}\nFRICTION={fric}\nDAMPING=0\nWAV='+('grass.wav' if key=='GRASS' else '')+f'\nWAV_PITCH=0\nFF_EFFECT=NULL\nDIRT_ADDITIVE={dirt}\nBLACK_FLAG_TIME=0\nIS_VALID_TRACK={valid}\nSIN_HEIGHT=0\nSIN_LENGTH=0\nIS_PITLANE=0\nVIBRATION_GAIN={vib}\nVIBRATION_LENGTH=0.6\n\n'
(D/'surfaces.ini').write_text(surf);(D/'lighting.ini').write_text('[LIGHTING]\nSUN_PITCH_ANGLE=40\nSUN_HEADING_ANGLE=45\n');(D/'groove.ini').write_text('[HEADER]\nGROOVES_NUMBER=0\n')
ui={'name':'SRT Michigan Autocross - MATLAB Loop','description':'137 original estimated MATLAB cones and 744.61 m event route, plus the existing 198.67 m synthetic return. Sector 1 spans the original 699.87 m timed portion. White 4 m route guides are visual only; cyan guides mark the synthetic return. Flat training reconstruction, not a surveyed venue. Cones are visual only, as in MATLAB; no cone penalties. Single-car practice recommended.','tags':['autocross','Formula Student','SRT','practice'],'country':'USA','city':'Michigan (estimated course)','length':str(round(station[-1]))+' m','width':'Open pad; 4 m visual guides','pitboxes':'1','run':'clockwise','version':'0.1','author':'Sooner Racing Team / SRT project'};(T/'ui/ui_track.json').write_text(json.dumps(ui,indent=2))
# Original replay and start cameras using the installed Kunos v3 INI schema.
def camera_ini(samples,title):
 text='[HEADER]\nVERSION=3\nCAMERA_COUNT='+str(len(samples))+'\nSET_NAME='+title+'\n\n'
 for i,ss0 in enumerate(samples):
  target,direction=at(ss0);side=np.array([direction[2],0,-direction[0]]);cam=target+side*12-direction*8+np.array([0,6,0]);forward=unit(target+np.array([0,.5,0])-cam);right=unit(np.cross(forward,[0,1,0]));up=np.cross(right,forward)
  text+=f'[CAMERA_{i}]\nNAME=SRT view {i+1}\nPOSITION='+','.join(map(str,cam))+'\nFORWARD='+','.join(map(str,forward))+'\nUP='+','.join(map(str,up))+f'\nMIN_FOV=20\nMAX_FOV=65\nIN_POINT={i/len(samples)}\nOUT_POINT={(i+1)/len(samples)}\nSHADOW_SPLIT0=30\nSHADOW_SPLIT1=100\nSHADOW_SPLIT2=400\nNEAR_PLANE=0.1\nFAR_PLANE=3000\nMIN_EXPOSURE=0.2\nMAX_EXPOSURE=0.6\nDOF_FACTOR=0\nDOF_RANGE=10000\nDOF_FOCUS=0\nDOF_MANUAL=0\nSPLINE=\nSPLINE_ROTATION=0\nFOV_GAMMA=1\nSPLINE_ANIMATION_LENGTH=15\nIS_FIXED=0\n\n'
 return text
(D/'cameras.ini').write_text(camera_ini([timing[0]+i*station[-1]/4 for i in range(4)],'SRT Autocross'))
(D/'cameras_start.ini').write_text(camera_ini([0],'SRT Start').replace('IN_POINT=0.0','IN_POINT=-1').replace('OUT_POINT=1.0','OUT_POINT=-1'))
# Original overhead previews and AC map; coordinate mapping follows map.ini offsets.
scale=max((hi[0]-lo[0])/1400,(hi[2]-lo[2])/1000);W=int(np.ceil((hi[0]-lo[0])/scale))+40;H=int(np.ceil((hi[2]-lo[2])/scale))+40
project=lambda pts:[((x-lo[0])/scale+20,(z-lo[2])/scale+20) for x,y,z in pts]
mapim=Image.new('RGBA',(W,H));dr=ImageDraw.Draw(mapim);dr.line(project(path),fill=(255,255,255,255),width=5);mapim.save(T/'map.png');(D/'map.ini').write_text(f'[PARAMETERS]\nWIDTH={W}\nHEIGHT={H}\nMARGIN=20\nSCALE_FACTOR={scale}\nMAX_SIZE=1600\nX_OFFSET={-lo[0]}\nZ_OFFSET={-lo[2]}\nDRAWING_SIZE=5\n');outline=mapim.copy();outline.thumbnail((480,480));outline_canvas=Image.new('RGBA',(512,512));outline_canvas.paste(outline,((512-outline.width)//2,(512-outline.height)//2));outline_canvas.save(T/'ui/outline.png')
im=Image.new('RGB',(W,H),(42,48,53));dr=ImageDraw.Draw(im);dr.line(project(path[:len(q)]),fill=(228,232,231),width=3);dr.line(project(path[len(q)-1:]),fill=(51,181,194),width=3)
for p in project(cone_pos):dr.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill=(255,126,36))
for label,s in [('TIMED START',timing[0]),('TIMED FINISH',timing[1])]:p=project([at(s)[0]])[0];dr.text(p,label,fill='white')
im=im.transpose(Image.Transpose.ROTATE_90);canvas=Image.new('RGB',(1440,650),(24,28,32));im.thumbnail((1380,480));canvas.paste(im,((1440-im.width)//2,105));dd=ImageDraw.Draw(canvas);font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',26);dd.text((32,24),'SRT MICHIGAN AUTOCROSS | MATLAB course transfer',fill='white',font=font);dd.text((32,62),'137 cones | 943.28 m loop | white: event route | cyan: synthetic return',fill=(165,210,215),font=font);dd.text((32,595),'Estimated flat layout. Cone positions preserved; guides are not legal boundaries.',fill=(175,181,186),font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',21));canvas.save(R/'track-overview.png');canvas.resize((1024,462)).save(T/'ui/preview.png')

np.savez_compressed(R/'geometry.npz',**{str(i):m['a'] for i,m in enumerate(meshes)});(R/'mesh-index.json').write_text(json.dumps([{'name':m['name'],'mat':m['mat'],'collision':m['collide']} for m in meshes]));(R/'course-export.json').write_text(json.dumps({'native_to_ac':'[-Z,Y,X] proper rotation, meters','path_ac_m':path.tolist(),'station_m':station.tolist(),'cones':cone_bounds,'timing_stations_m':timing,'helpers':{n:x.tolist() for n,x in helpers}},indent=2))
report={'source_sha256':hashlib.sha256(raw).hexdigest(),'source_is_survey':False,'upright':sum(c['role']=='upright' for c in C['cones']),'fallen':sum(c['role']!='upright' for c in C['cones']),'original_points':len(q),'closed_points':len(path),'original_length_m':orig_s[-1],'return_length_m':station[-1]-orig_s[-1],'lap_length_m':station[-1],'original_timed_distance_m':timing[1]-timing[0],'mesh_count':len(meshes),'triangles':sum(len(m['a'])//3 for m in meshes),'model_sha256':hashlib.sha256(buf.getvalue()).hexdigest(),'asphalt_bounds_m':[lo.tolist(),hi.tolist()],'limits':['Flat terrain assumed; no survey elevation','Cones visual only; no collisions or penalties, matching MATLAB','4 m paint guides are not course boundaries','Original event estimates and synthetic return retain original uncertainty','AI line supports map and timing; AI pace and racing not validated']};(R/'build-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
