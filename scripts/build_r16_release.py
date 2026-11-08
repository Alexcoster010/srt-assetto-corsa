from pathlib import Path
import zipfile,json,hashlib,configparser,math,sys
P=Path(__file__).resolve().parents[1];R=P/'release-r16';R.mkdir(exist_ok=True);D=R/'download';D.mkdir(exist_ok=True);prefix='content/cars/srt27_prototype/'
base=R/'baseline-r15.zip';assert hashlib.sha256(base.read_bytes()).hexdigest()=='04aecac47f378f6981424cf33e0986519aab8ac3e94079ec16c7091de0b86cf0'
with zipfile.ZipFile(base) as z:
 raw={name:z.read(name) for name in z.namelist()}
 setup=raw[prefix+'data/setup.ini'].decode();ui=json.loads(raw[prefix+'ui/ui_car.json']);sus=configparser.ConfigParser();sus.read_string(raw[prefix+'data/suspensions.ini'].decode());assert b'VERSION=extended-1' in raw[prefix+'data/car.ini']
controls=[]
def item(section,tab,name,lo,hi,step,x,y,default,helpkey,extra=''):
 global setup
 assert lo<=default<=hi and abs((default-lo)/step-round((default-lo)/step))<1e-6,(section,default)
 setup+=f'\n[{section}]\nSHOW_CLICKS=0\nTAB={tab}\nNAME={name}\nMIN={lo:.12f}\nMAX={hi:.12f}\nSTEP={step:.12f}\nPOS_X={x}\nPOS_Y={y}\nHELP={helpkey}\n'+extra
 controls.append({'section':section,'tab':tab,'name':name,'min':lo,'max':hi,'step':step,'default':default})
item('CUSTOM_SCRIPT_ITEM_0','AERO','Aero balance - front %',30,50,1,.5,1,40,'More front increases front downforce and reduces rear. Total nominal downforce and drag unchanged. Default40.', 'ID=SRT_AERO_BALANCE\nDEFAULT=40\n')
for axle,side,x in [('FRONT','LF',0),('FRONT','RF',1),('REAR','LR',0),('REAR','RR',1)]:
 rear=axle=='REAR';row=6 if rear else 1;k=sus.getfloat(axle,'SPRING_RATE')/1000;rod=sus.getfloat(axle,'ROD_LENGTH')*1000
 item('SPRING_RATE_'+side,'SUSPENSION','Wheel rate '+side+' (N/mm)',k-(16 if rear else 10),k+20,1,x,row,k,'HELP_'+side+'_WHEELRATE')
 item('ROD_LENGTH_'+side,'SUSPENSION','Ride-height adjust '+side,rod-10,rod+10,1,x,row+1,rod,'HELP_'+side+'_RODLENGTH')
 item('CAMBER_'+side,'ALIGNMENT','Camber '+side,-4,1,.1,x,6 if rear else 0,0,'HELP_'+side+'_CAMBER')
 item('TOE_OUT_'+side,'ALIGNMENT','Toe adjust '+side,-10,10,1,x,7 if rear else 1,0,'HELP_'+side+'_TOE')
 for j,(key,lo,hi,step,helpkey) in enumerate([('DAMP_BUMP',800,3200,100,'BUMP'),('DAMP_FAST_BUMP',300,1800,100,'FBUMP'),('DAMP_REBOUND',1000,4000,100,'REBOUND'),('DAMP_FAST_REBOUND',400,2400,100,'REBOUND')]):
  item(key+'_'+side,'DAMPERS',key.replace('DAMP_','').replace('_',' ').title()+' '+side,lo,hi,step,x,j+(5 if rear else 0),sus.getfloat(axle,key),'HELP_'+side+'_DAMPER_'+helpkey)
for axle,row in [('FRONT',0),('REAR',8)]:item('ARB_'+axle,'SUSPENSION','Anti-roll bar '+axle.lower(),0,15000,500,.5,row,0,'HELP_'+axle+'_ARB')
script='''-- SRT r16: one pit-setup slider redistributes existing wing lift.
-- Reference: CSP ac.getScriptSetupValue and ac.setWingGain API.
-- No new forces, no powertrain/suspension overrides, no saved-setup writes.
local launchUpdate = script.update
local balanceRef = ac.getScriptSetupValue('CUSTOM_SCRIPT_ITEM_0')
function script.update(dt)
  if launchUpdate then launchUpdate(dt) end
  if balanceRef == nil then
    balanceRef = ac.getScriptSetupValue('CUSTOM_SCRIPT_ITEM_0')
  end
  local percent = balanceRef and balanceRef.value or 40
  if type(percent) ~= 'number' or percent ~= percent then percent = 40 end
  percent = math.max(30, math.min(50, percent))
  local front = percent / 100
  ac.setWingGain(0, 1, front / 0.40)
  ac.setWingGain(1, 1, (1 - front) / 0.60)
end
'''
script=raw[prefix+'data/script.lua'].decode()+'\n'+script
# Execute the shipped Lua, with CSP API calls mocked; not an AC runtime test.
sys.path.insert(0,str(R/'test-tools'));from lupa import LuaRuntime
lua=LuaRuntime();lua.execute('script={}; car={speedKmh=0,clutch=0,gear=1}; ref={value=40}; calls={}; available=true; ac={setEngineRPMLimit=function(rpm,scale) limit=rpm end, getScriptSetupValue=function(id) assert(id=="CUSTOM_SCRIPT_ITEM_0"); if available then return ref else return nil end end, setWingGain=function(i,cd,cl) calls[i]={cd=cd,cl=cl} end}')
lua.execute(script);g=lua.globals();tested=[]
for value in list(range(30,51))+[0,100,float('nan')]:
 g.ref.value=value;g.script.update(.003);expect=40 if math.isnan(value) else min(50,max(30,value));f=g.calls[0];r=g.calls[1]
 assert abs(f.cl*1.04+r.cl*1.56-2.6)<1e-12;assert abs(f.cl*1.04/2.6-expect/100)<1e-12;assert f.cd==r.cd==1;tested.append(expect)
g.car.gear=2;g.car.clutch=1;g.script.update(.003);assert g.limit==8000
g.car.clutch=0;g.script.update(.003);assert g.limit==16000
g.script.reset();assert g.limit==16000
g.available=False;lua.execute(script);g.script.update(.003);assert g.calls[0].cl==1 and g.calls[1].cl==1
g.available=True;g.ref.value=45;g.script.update(.003);assert abs(g.calls[0].cl-1.125)<1e-12
# Check every angle knot: gain redistribution approximately preserves the baseline total LUT.
cl=[]
for i in [0,1]:cl.append([[float(v) for v in l.split('|')] for l in raw[prefix+f'data/srt_aero_{i}_cl.lut'].decode().splitlines() if '|' in l])
maxerr=0
for a,b in zip(*cl):
 assert a[0]==b[0]
 for pct in range(30,51):maxerr=max(maxerr,abs(a[1]*pct/40+b[1]*(100-pct)/60-(a[1]+b[1])))
assert maxerr<1e-7
ui.update(version='0.16.0',description='r16 setup test: AERO front-balance slider30-50%, default40%. Suspension, alignment and damper adjustments unlocked. Defaults retain r15 physics and r14 softer rear. Requires CSP0.2.11 with extended physics. Runtime UI/driver verification pending.')
guide='''# SRT r16 setup guide

In the session pits, open Setup (wrench). Adjust AERO, SUSPENSION, ALIGNMENT and DAMPERS, save a named setup, and drive another run. These are pit setup controls, not an on-wheel live tuning app. Use Reset/Default for the r15 starting setup; avoid loading an older custom setup when comparing defaults.

## AERO
One slider: **Aero balance - front %**,30-50 in1 percentage-point steps; default40. Rear share is100 minus front. Higher values shift load forward; lower values shift it rearward. The script scales the existing front/rear lift gains, with nominal total CL*A2.60m2 and unchanged drag gains. Default40 produces unity gains, retaining the r15 aero. Local flow at each wing can differ in motion, so the displayed percentage is nominal, not measured instantaneous axle loading. This is still the preliminary aero model, not a measured aero map. Visual wing angles do not move.

## SUSPENSION
Four wheel-rate sliders (N/mm); front default27.235425, rear36.593879. Front range17.235425-47.235425, rear20.593879-56.593879; steps1N/mm. Decimal offsets keep the exact r15 rates on the adjustment grid. Front/rear anti-roll bars0-15000 in500 steps, default0; experimental tuning range, not verified real hardware. Ride-height adjustment uses suspension rod length, +/-10mm about each baseline; rod-length change is not equal to actual chassis ride-height change. Check the live car height/travel values. Front rod baseline21.359331mm, rear12.180235mm.

## ALIGNMENT AND DAMPERS
Four camber sliders -4 to+1deg in0.1 steps, default0. Toe controls -10 to+10 native adjustment units, default0: these are steering-link offsets, NOT degrees of wheel toe. Check the resulting alignment readout. Slow bump800-3200 (default1800), fast bump300-1800 (default900), rebound1000-4000 (default2400), fast rebound400-2400 (default1200), in100N*s/m steps. Match left and right when testing basic balance. Native setups may allow asymmetric tuning; there is no automatic axle linking.

Start by changing aero one or two points, or one axle's spring rate one step on both sides. Save each comparison separately. R15 engine curve, upshift settings, tires, FFB, brakes, differential, CG and suspension default values are retained. Existing brake-bias/differential controls remain available.

Requires CSP0.2.11 (same as prior car) with extended physics enabled; car.ini already uses extended-1. If AERO control is absent or nonfunctional, check CSP and report it; without physics scripting the base aero remains40/60. A normal Lua app checkbox is not needed: data/script.lua is the car physics script.

Validation: Lua executed with mocked CSP calls across all21 aero settings, default, out-of-range inputs, missing setup ref and delayed ref availability. Lift sum/drag gains checked; all native control defaults lie within range and on their grids. Existing physics files remain byte-identical to r15 except setup.ini and script.lua; the original launch-limiter script is preserved with an appended aero wrapper. This does NOT prove menu rendering, native setup scaling, save/reload behavior, or in-game load; these require sim testing. No car reinstalled on the laptop.
'''
notes='''# SRT r16 â€” adjustable aero and suspension

Test release. Adds35 setup controls while retaining r15 default physics: single front aero-balance slider30-50% (default40), four wheel spring rates, front/rear anti-roll bars, four ride-height rod adjustments, camber/toe and slow/fast bump/rebound dampers. See SETUP_GUIDE_r16.md for ranges and meaning.

Full car: extract into the Assetto Corsa root and overwrite the existing SRT car. Small patch: apply only over r15. Restart session and use Setup in the pits; Reset/Default before establishing a baseline. UI version0.16.0. Requires CSP0.2.11 and extended physics. R15 torque/shift changes and r14 softer rear remain the defaults. Save named setups for comparison.

Offline script/config/package checks passed. In-game UI, persistence and handling are not yet verified. This is a test version, not calibrated hardware adjustment ranges.

Rollback: reinstall r15, including its original data/script.lua and setup.ini, then reset setup. Keep old release downloads for comparison.
'''
(R/'SETUP_GUIDE.md').write_text(guide);(R/'RELEASE_NOTES.md').write_text(notes)
over={'data/setup.ini':setup.encode(),'data/script.lua':script.encode(),'ui/ui_car.json':(json.dumps(ui,indent=2)+'\n').encode(),'SETUP_GUIDE_r16.md':guide.encode(),'RELEASE_r16.md':notes.encode()}
for name,b in over.items():
 f=R/'content/cars/srt27_prototype'/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
cfg=configparser.ConfigParser(strict=True);cfg.read_string(setup);assert len(controls)==35
positions=set()
for c in controls:
 sec=cfg[c['section']];pos=(sec['TAB'],sec['POS_X'],sec['POS_Y']);assert pos not in positions;positions.add(pos)
changes=[name.removeprefix(prefix) for name,b in raw.items() if name.removeprefix(prefix) in over and b!=over[name.removeprefix(prefix)]];assert set(changes)=={'data/setup.ini','data/script.lua','ui/ui_car.json'}
manifest={};archive=D/'SRT_2025-2026_r16_Assetto_Corsa.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,b in raw.items():
  b=over.get(name.removeprefix(prefix),b);z.writestr(name,b);manifest[name]=hashlib.sha256(b).hexdigest()
 for name,b in over.items():
  if prefix+name not in raw:z.writestr(prefix+name,b);manifest[prefix+name]=hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(archive) as z:
 for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
patch=D/'SRT_r15_to_r16_Test_Patch.zip'
with zipfile.ZipFile(patch,'w',zipfile.ZIP_DEFLATED) as z:
 for name,b in over.items():z.writestr(prefix+name,b)
validation={'controls':controls,'lua_mock_checks':'pass; not AC runtime','aero_settings_tested':21,'nominal_total_cl_area':2.6,'max_lut_total_error':maxerr,'baseline_existing_changes':changes,'base_physics_INIs_except_setup_identical_to_r15':True,'launch_limiter_regression':'8000rpm armed/16000rpm released/reset passed in mocked Lua','runtime_tested':False,'package_hashes_verified':True,'sources':['Kunos SDK dev/content/cars/formula_k/data/setup.ini','Installed CSP0.2.11 internal/lua-sdk/ac_car_cphys/lib.lua','https://github.com/ac-custom-shaders-patch/acc-extension-config/wiki/Cars-%E2%80%93-Physics-scripts']}
(R/'validation.json').write_text(json.dumps(validation,indent=2));(R/'file-manifest.json').write_text(json.dumps(manifest,indent=2));info={'version':'0.16.0','archive':str(archive.resolve()),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'zip_verified':True,'driver_validation':'pending'};(D/'package.json').write_text(json.dumps(info,indent=2));(D/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in [archive,patch]));print(json.dumps({'controls':len(controls),'lua_checks':'passed','lut_error':maxerr,**info},indent=2))
