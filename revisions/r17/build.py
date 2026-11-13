from pathlib import Path
import json,struct,io,zipfile,hashlib,sys,itertools,collections
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;P=R.parent;sys.path.insert(0,str(R/'test-tools'));from scipy.spatial import ConvexHull
ns={};exec((R/'audit.py').read_text().split("with zipfile.ZipFile(R/")[0],ns);parse=ns['parse']
base=R/'baseline-r16.zip';expected=json.loads((P/'release-r16/download/published.json').read_text())['sha256'];assert hashlib.sha256(base.read_bytes()).hexdigest()==expected
with zipfile.ZipFile(base) as z:raw={n:z.read(n) for n in z.namelist()}
prefix='content/cars/srt27_prototype/';model=raw[prefix+'srt27_prototype.kn5'];meta=parse(model);over={}
def pack(fmt,*v):return struct.pack('<'+fmt,*v)
def string(s):b=s.encode();return pack('i',len(b))+b
def node(name,count):return pack('i',1)+string(name)+pack('iB',count,1)+pack('16f',1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)
def mesh(name,tri,mat):
 tri=np.asarray(tri);norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm/=np.linalg.norm(norm,axis=1)[:,None];v=np.c_[tri.reshape(-1,3),np.repeat(norm,3,axis=0),np.tile([[0,0],[1,0],[1,1]],(len(tri),1)),np.tile([1,0,0],(len(tri)*3,1))].astype('<f4');n=len(v)
 return pack('i',2)+string(name)+pack('i4Bi',0,1,1,1,0,n)+v.tobytes()+pack('i',n)+np.arange(n,dtype='<u2').tobytes()+pack('II6fB',mat,0,0,2000,0,0,0,3,1)
def material(name,shader='ksPerPixel',texture=None):
 props={'ksAmbient':.35,'ksDiffuse':.65,'ksSpecular':.2,'ksSpecularEXP':20,'ksEmissive':0,'ksAlphaRef':0} if shader!='GL' else {}
 b=string(name)+string(shader)+pack('BBi',0,0,0)+pack('i',len(props))
 for k,v in props.items():b+=string(k)+pack('10f',v,*([0]*9))
 b+=pack('i',int(texture is not None))
 if texture:b+=string('txDiffuse')+pack('i',0)+string(texture)
 return b
def dds(color):
 b=io.BytesIO();Image.new('RGB',(4,4),color).save(b,format='DDS');return b.getvalue()
# Rear-facing lamp lens under rear wing. Position is an illustrative mount, not measured team hardware.
lens=np.array([[[-.06,.58,-1.002],[.06,.63,-1.002],[.06,.58,-1.002]],[[-.06,.58,-1.002],[-.06,.63,-1.002],[.06,.63,-1.002]]])
# Winding points toward rear (-Z).
assert np.cross(lens[0,1]-lens[0,0],lens[0,2]-lens[0,0])[2]<0
lamptex=dds((140,4,2));tx=pack('i',1)+string('SRT_BRAKE_LENS.dds')+pack('i',len(lamptex))+lamptex
mp=meta['material_count_offset'];rp=meta['root_offset'];root=bytearray(model[rp:]);co=meta['root_children_offset']-rp;struct.pack_into('<i',root,co,struct.unpack_from('<i',root,co)[0]+1)
newmodel=model[:meta['texture_count_offset']]+pack('i',meta['texture_count']+1)+model[meta['texture_count_offset']+4:mp]+tx+pack('i',meta['material_count']+1)+model[mp+4:rp]+material('SRT_BRAKE_LENS',texture='SRT_BRAKE_LENS.dds')+root+mesh('SRT_BRAKE_LIGHT',lens,meta['material_count'])
newmeta=parse(newmodel);assert len(newmeta['meshes'])==len(meta['meshes'])+1
for a,b in zip(meta['meshes'],newmeta['meshes']):assert a==b
assert newmeta['meshes'][-1]['name']=='SRT_BRAKE_LIGHT'
over['srt27_prototype.kn5']=bytes(newmodel);over['data/lights.ini']=b'[HEADER]\nVERSION=3\n\n[BRAKE_0]\nNAME=SRT_BRAKE_LIGHT\nCOLOR=200,2,0\nOFF_COLOR=0,0,0\n'
# Single low-poly convex shell following major vehicle extents; no individual CAD surfaces.
outline=[(-.495,-1.002),(.495,-1.002),(.66,-.82),(.66,1.30),(.635,1.912),(-.635,1.912),(-.66,1.30),(-.66,-.82)]
pts=[[x,.055,z] for x,z in outline]
pts += [[x,.455,z] for x,z in [(-.66,-.82),(.66,-.82),(-.66,1.30),(.66,1.30)]]
pts += [[x,y,z] for x in [-.495,.495] for y in [.64,1.17] for z in [-1.002,-.227]]
pts += [[x,1.075,z] for x in [-.22,.22] for z in [-.1,.30]]
pts += [[x,.52,1.65] for x in [-.18,.18]]
pts=np.array(pts);h=ConvexHull(pts);tri=pts[h.simplices].copy()
for i,t in enumerate(tri):
 if np.dot(np.cross(t[1]-t[0],t[2]-t[0]),h.equations[i,:3])<0:tri[i]=t[[0,2,1]]
assert len(tri)<=60
edges=collections.Counter()
for t in h.simplices:
 for a,b in zip(t,np.roll(t,-1)):edges[tuple(sorted([int(a),int(b)]))]+=1
assert set(edges.values())=={2};vol=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert vol>0 and abs(vol-h.volume)<1e-8
coll=b'sc6969'+pack('iii',5,0,1)+material('GL','GL')+node('SRT_ROOT',1)+node('COLLIDER_TRANSFORM',1)+mesh('COLLIDER',tri,0);cm=parse(coll);assert cm['texture_count']==0;over['collider.kn5']=coll
# Keep asphalt/kerb ground box and all handling physics untouched in this first isolation test.
colors=[('White Black',(235,236,238)),('Crimson',(150,18,40)),('Royal Blue',(25,60,210)),('Sky Blue',(40,180,245)),('Green',(20,125,65)),('Lime',(150,225,20)),('Orange',(245,105,12)),('Yellow',(245,215,20)),('Purple',(110,45,185)),('Magenta',(220,35,140)),('Teal',(0,160,155)),('Silver',(155,165,180))]
for i,(name,color) in enumerate(colors):
 folder=f'skins/r17_{i+1:02d}_'+name.lower().replace(' ','_');over[folder+'/SRT_WHITE.dds']=dds(color)
 over[folder+'/ui_skin.json']=(json.dumps({'skinname':f'R17 {i+1:02d} - '+name,'drivername':'','country':'USA','number':'31'},indent=2)+'\n').encode()
 im=Image.new('RGB',(64,64),color);dr=ImageDraw.Draw(im);dr.rectangle((0,45,63,63),fill=(25,27,29));b=io.BytesIO();im.save(b,format='PNG');over[folder+'/livery.png']=b.getvalue()
 # Clearly labelled color cards, not inaccurate renders of the car.
 im=Image.new('RGB',(1024,576),(25,27,29));dr=ImageDraw.Draw(im);dr.rounded_rectangle((80,80,944,410),radius=40,fill=color);dr.text((100,450),f'SRT r17 | {i+1:02d} {name} | COLOR SELECTION CARD',fill='white',font_size=27);b=io.BytesIO();im.save(b,format='JPEG',quality=90);over[folder+'/preview.jpg']=b.getvalue()
ui=json.loads(raw[prefix+'ui/ui_car.json']);ui.update(version='0.17.0',description='r17 test: rear brake light, broader closed low-poly collision envelope and12 driver-color skins. R16 engine/suspension/aero controls unchanged. Collision runaway/crash fix NOT runtime-verified. CSP0.2.11 required.');over['ui/ui_car.json']=(json.dumps(ui,indent=2)+'\n').encode()
notes=f'''# SRT r17 â€” brake light, collision coverage and driver colors

Test build November 12, 2026. Includes r16 tuning controls and all existing engine/handling settings.

Rear brake light: new120x50mm rear-facing red lens centered under the rear wing, driven by brake input using Kunos lights.ini v3. It is off with brakes released, independent of headlights. Mount location is illustrative, not a verified team-CAD brake lamp.

Collision coverage: r16's collider was only0.64m wide,0.30m high and1.83m long, leaving much of the wheels/sidepods/wings/upper chassis outside. Replaced it with one closed convex shell spanning1.32m wide,1.115m high and2.914m long, {len(tri)} triangles, GL material/no textures, identity transforms. Minimum model Y0.055m stays above the frame floor near0.0508m. Tires' bottom contact region and the lowest17mm of front wing are intentionally not added below the floor. This is a simplified envelope: it fills gaps between parts and does not provide independent deformable wheel/wing collision. Visual parts are not separate crash bodies.

The previous mesh was already closed with valid transforms; missing coverage is confirmed, but the cause of runaway spins/game crashes is NOT proven. This build addresses coverage and deep overlap risk, not a demonstrated solver fix. Mass/inertia, ground box, engine, tire, suspension, brake and aero physics are unchanged. Thin/non-collidable track barriers and high-speed tunnelling cannot be guaranteed fixed by a car mesh. Reproduce low-speed contacts before escalating speed; compare the same barrier/car with r16. Record track/layout, speed, impact side, and whether the same barrier fails with a stock car. If it crashes again, preserve logs/crash dump and stop that test. No artificial angular-velocity clamp is included.

12 NEW selectable skins: White/Black, Crimson, Royal Blue, Sky Blue, Green, Lime, Orange, Yellow, Purple, Magenta, Teal and Silver. Select an R17 skin in Content Manager before joining; each driver selects a different one. Overrides existing white-painted body/wing elements; carbon areas, number31 and brake-light red are unchanged. These are colors, not editable racing numbers. Previews are explicitly labelled color cards, not rendered car views. Existing skins remain available.

Install full car ZIP into Assetto Corsa root, overwrite and restart. There is no small patch because the brake-light mesh changes the main117MB KN5. UI version0.17.0. Requires CSP0.2.11. Back up your setup; reset to baseline when comparing collision behavior. Rollback: reinstall r16 including model/collider/lights.ini; extra r17 skin folders can remain or be removed.

Validation: binary readback/EOF, preserved120 original mesh bounds/material assignments, brake mesh reference, convexity/watertight edges/positive volume/triangle budget, archive checksums and unchanged physics allowlist. Visual brake response and actual collisions are NOT runtime-tested; no crash-fix claim. Kunos SDK AC Pipeline Rev2.0 pages28/36 and colliders.ini comments were used as primary references.
'''
(R/'RELEASE_NOTES.md').write_text(notes);over['RELEASE_r17.md']=notes.encode()
# Simple projected collision diagnostic and color palette, generated from geometry.
im=Image.new('RGB',(1300,780),'white');dr=ImageDraw.Draw(im);dr.text((35,20),'SRT r17 collision envelope - geometry check (not an in-game view)',fill='black',font_size=25)
def project(p,side):
 if side:return (75+(p[2]+1.1)*330,470-p[1]*310)
 return (75+(p[2]+1.1)*330,670-p[0]*100)
for side in [True,False]:
 for a,b in edges:
  pa,pb=project(pts[a],side),project(pts[b],side);dr.line([pa,pb],fill=(180,30,45),width=2)
dr.text((45,70),'Side',fill='black',font_size=20);dr.text((45,535),'Top',fill='black',font_size=20)
for i,(name,color) in enumerate(colors):
 x=1090;y=65+i*54;dr.rectangle((x,y,x+65,y+32),fill=color,outline='black');dr.text((x+72,y+6),name,fill='black',font_size=13)
im.save(R/'geometry-and-colors.png')
D=R/'download';D.mkdir(exist_ok=True);archive=D/'SRT_2025-2026_r17_Assetto_Corsa.zip';manifest={};changed=[]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,b in raw.items():
  rel=name.removeprefix(prefix);new=over.get(rel,b)
  if new!=b:changed.append(rel)
  z.writestr(name,new);manifest[name]=hashlib.sha256(new).hexdigest()
 for name,b in over.items():
  if prefix+name not in raw:z.writestr(prefix+name,b);manifest[prefix+name]=hashlib.sha256(b).hexdigest()
assert set(changed)=={'srt27_prototype.kn5','collider.kn5','data/lights.ini','ui/ui_car.json'},changed
with zipfile.ZipFile(archive) as z:
 for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
for name in ['srt27_prototype.kn5','collider.kn5','data/lights.ini']:
 if name.endswith('.kn5'):continue
 f=R/'content/cars/srt27_prototype'/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(over[name])
validation={'changed_existing_files':changed,'all_handling_physics_unchanged':True,'original_meshes_preserved':120,'brake_light_mesh':'SRT_BRAKE_LIGHT','collision_triangle_count':len(tri),'collision_watertight':True,'collision_convex':True,'collision_volume_m3':vol,'collision_bounds':cm['meshes'][0],'new_driver_skins':len(colors),'runtime_tested':False,'runaway_spin_cause':'unconfirmed','zip_verified':True};(R/'validation.json').write_text(json.dumps(validation,indent=2));(R/'file-manifest.json').write_text(json.dumps(manifest,indent=2));info={'version':'0.17.0','archive':str(archive.resolve()),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'zip_verified':True,'driver_validation':'pending'};(D/'package.json').write_text(json.dumps(info,indent=2));(D/'SHA256SUMS.txt').write_text(info['sha256']+'  '+archive.name+'\n');print(json.dumps(validation,indent=2))
