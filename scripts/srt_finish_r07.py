from pathlib import Path
import os,json,configparser,hashlib,shutil,numpy as np
P=Path(os.environ.get('SRT_AC_PROJECT',str(Path(__file__).resolve().parents[1])));R=P/'release-r07';O=R/'content/cars/srt27_prototype'
def edit(name,sections):
 p=O/'data'/name;c=configparser.ConfigParser(strict=False,inline_comment_prefixes=(';',));c.optionxform=str;c.read(p)
 for s,d in sections.items():
  if not c.has_section(s):c.add_section(s)
  c[s].update({k:str(v) for k,v in d.items()})
 with p.open('w') as h:c.write(h,space_around_delimiters=False)
edit('car.ini',{'INFO':{'SCREEN_NAME':'Sooner Racing Team 2025-2026 No.31'},'GRAPHICS':{'DRIVEREYES':'0,0.84,0.22','ON_BOARD_PITCH_ANGLE':0}})
edit('dash_cam.ini',{'DASH_CAM':{'POS':'0,0.79,0.27'}})
edit('electronics.ini',{'ABS':{'SLIP_RATIO_LIMIT':.12,'CURVE':'','RATE_HZ':250},'TRACTION_CONTROL':{'SLIP_RATIO_LIMIT':.1,'MIN_SPEED_KMH':40,'CURVE':'','RATE_HZ':100}})
edit('flames.ini',{'HEADER':{'INTENSITY':0}})
edit('lods.ini',{'COCKPIT_HR':{'DISTANCE_SWITCH':0}})
edit('ai.ini',{'GEARS':{'UP':14500,'DOWN':8500,'GAS_CUTOFF_TIME':.08},'ULTRA_GRIP':{'VALUE':1.0}})
gear_cfg=configparser.ConfigParser();gear_cfg.read(O/'data/drivetrain.ini')
edit('setup.ini',{'GEARS':{'USE_GEARSET':0}})
for i in range(1,7):
 ratio=gear_cfg['GEARS']['GEAR_'+str(i)];filename='srt_fixed_gear_'+str(i)+'.rto';(O/'data'/filename).write_text('SRT '+str(i)+'|'+ratio+'\n');edit('setup.ini',{'GEAR_'+str(i):{'RATIOS':filename,'NAME':'Gear '+str(i)+' - fixed','POS_X':.5,'POS_Y':i-1,'HELP':'HELP_REAR_GEAR'}})
ui=json.loads((O/'ui/ui_car.json').read_text());ui.update(name='Sooner Racing Team 2025-2026 No.31',version='0.6',brand='Sooner Racing Team',description='Native team CAD frame, nose, wings, cockpit, wheels and mechanical parts. White/black No.31 livery and sidepod shells interpreted from 2026 unveiling photos. SRT r35 effective engine curve; provisional 60/42/25 differential mapping; 18 x 6 inch tires. Track behavior, driver pose, sidepods and aero remain approximations.');(O/'ui/ui_car.json').write_text(json.dumps(ui,indent=2))
for slug in ['00_crimson','01_srt_white_black']:
 skin=O/'skins'/slug;skin.mkdir(exist_ok=True);(skin/'ui_skin.json').write_text(json.dumps({'skinname':'SRT No.31 White / Black','drivername':'Sooner Racing Team','country':'USA','number':'31'},indent=2))
(O/'LOCAL_ASSET_PROVENANCE.txt').write_text('Native team CAD vehicle mesh and original procedural white/black livery. Sidepod shells inferred from public 2026 unveiling photos. No MAD car-body, wheel or cockpit mesh remains. Local temporary MAD driver pose/animations and Kunos driver/audio assets remain, so the installed game folder is not a public redistribution package. Original source CAD files unchanged.\n')
# Read geometry independently of builder state.
ms=json.loads((R/'meshes.json').read_text());g=np.load(R/'geometry.npz');tests={};alltri=[]
for group in ['WHEEL_LF','WHEEL_RF','WHEEL_LR','WHEEL_RR']:
 v=np.concatenate([g[str(i)][:,:3] for i,m in enumerate(ms) if m['group']==group and 'Tyre' in m['name']]);dims=np.ptp(v,axis=0);assert np.allclose(dims,[.1524,.4572,.4572],atol=2e-6);tests[group]={'width_m':float(dims[0]),'outside_diameter_y_m':float(dims[1]),'outside_diameter_z_m':float(dims[2])}
for i in range(len(ms)):alltri.append(g[str(i)][:,:3].reshape(-1,3,3))
t=np.concatenate(alltri);assert np.isfinite(t).all();e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];eye=np.array([0,.84,.22]);results=[]
for yaw,pitch in [(0,0),(-5,0),(5,0),(0,-5),(0,5)]:
 y,p=np.radians([yaw,pitch]);direction=np.array([np.sin(y)*np.cos(p),np.sin(p),np.cos(y)*np.cos(p)]);h=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,h);ok=abs(det)>1e-10;inv=np.zeros(len(t));inv[ok]=1/det[ok];s=eye-t[:,0];u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=inv*(q@direction);dist=inv*np.einsum('ij,ij->i',e2,q);hit=ok&(u>=0)&(v>=0)&(u+v<=1)&(dist>.002);nearest=float(dist[hit].min()) if hit.any() else None;results.append({'yaw_deg':yaw,'pitch_deg':pitch,'nearest_body_hit_m':nearest});assert nearest is None or nearest>.5
report={'tire_envelopes':tests,'camera_position_model_m':eye.tolist(),'camera_body_rays':results,'camera_limit':'Checks car geometry only; animated driver visibility and in-game framing still require visual confirmation.','finite_geometry':True,'geometry_bounds_m':[t.reshape(-1,3).min(0).tolist(),t.reshape(-1,3).max(0).tolist()]};(R/'geometry-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
