from pathlib import Path
import zipfile,json,hashlib,sys
R=Path(__file__).resolve().parent;P=R.parent;prefix='content/cars/srt27_prototype/';base=R/'baseline-r17.zip'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='de9a0e675b4603624a3b1a7deb6730aa7e305ba6e983f02fb714ea7d6088e876'
with zipfile.ZipFile(base) as z:raw={n:z.read(n) for n in z.namelist()}
script=raw[prefix+'data/script.lua'].decode()+'\n'+(R/'stint.lua').read_text()
sys.path.insert(0,str(P/'release-r16/test-tools'));from lupa import LuaRuntime
lua=LuaRuntime();lua.execute('''script={}; car={index=0,lapCount=0,speedKmh=20,clutch=0,gear=2,isInPit=false,wheels={}}; ph={wheels={},controllerInputs={}}; ref={value=40}; for i=0,3 do car.wheels[i]={tyreVirtualKM=1}; ph.wheels[i]={finalForceMult={x=1,y=1}} end; ac={accessCarPhysics=function() return ph end, getScriptSetupValue=function() return ref end, setEngineRPMLimit=function(v,s) limit=v end, setWingGain=function(i,cd,cl) end}''');lua.execute(script);g=lua.globals()
def step(n=100):
 for i in range(n):g.script.update(.02)
step();assert g.ph.controllerInputs[240]==0
for lap,expected in [(5,.995),(10,.98),(15,.90),(16,.80),(18,.60),(25,.60)]:
 g.car.lapCount=lap;step(250);assert abs(g.ph.controllerInputs[241]-expected)<1e-4
 for i in range(4):assert g.ph.wheels[i].finalForceMult.x==g.ph.wheels[i].finalForceMult.y
# pitlane / stop on track does not count as service
g.car.speedKmh=0;step(600);assert g.ph.controllerInputs[240]==25
# teleport/reset alone does not erase stint
g.script.reset();step();assert g.ph.controllerInputs[240]==25
# own-box stop: no early grant, reset after10 seconds
g.car.isInPit=True;step(450);assert g.ph.controllerInputs[240]==25
step(55);assert g.ph.controllerInputs[240]==0;step(250);assert g.ph.controllerInputs[241]>.999
# service latch and leave/re-enter behavior
g.car.isInPit=False;g.car.speedKmh=20;g.car.lapCount=30;step();assert g.ph.controllerInputs[240]==5
# native4-tire change before10 sec
g.car.isInPit=True;g.car.speedKmh=0
for i in range(4):g.car.wheels[i].tyreVirtualKM=0
step(1);assert g.ph.controllerInputs[240]==0
# no second aging on repeated lap samples; new session lap decrease resets
g.car.isInPit=False;g.car.speedKmh=20;g.car.lapCount=45;step();assert g.ph.controllerInputs[240]==15
step();assert g.ph.controllerInputs[240]==15
g.car.lapCount=0;step();assert g.ph.controllerInputs[240]==0
# original launch limiter still works
g.car.speedKmh=0;g.car.gear=2;g.car.clutch=1;g.script.reset();step(1);assert g.limit==8000
g.car.clutch=0;step(1);assert g.limit==16000
hud='''function script.windowMain(dt)
  local p=ac.getCarPhysics(0)
  if p==nil or p.scriptControllerInputs[243]~=18 then
    ui.text('SRT r18 tire-stint data unavailable')
    return
  end
  local d=p.scriptControllerInputs
  ui.text(string.format('Tire stint: %d / 15 laps',d[240]))
  ui.text(string.format('Game-rule grip: %.1f%%',d[241]*100))
  if d[244]>0 then ui.text('New set ready')
  elseif d[242]>0 then ui.text(string.format('Pit service: %.1f / 10 seconds',d[242]))
  elseif d[240]>=15 then ui.text('PIT FOR A NEW SET')
  elseif d[240]>=13 then ui.text('Pit stop approaching') end
end
'''
manifest='[ABOUT]\nNAME=SRT Tire Stint\nAUTHOR=SRT project\nVERSION=0.18.0\nDESCRIPTION=15-lap tire-stint counter and pit service timer\n\n[WINDOW_0]\nID=main\nNAME=SRT Tire Stint\nFUNCTION_MAIN=windowMain\nSIZE=300,140\n'
# Parse Lua HUD too, with a test UI and state.
lua.execute('ui={text=function(x) end}; ac.getCarPhysics=function(i) return {scriptControllerInputs=ph.controllerInputs} end');lua.execute(hud);g.script.windowMain(.02)
notes='''# SRT r18 â€” 15-lap race tire rule

November12,2026. Requested gameplay degradation, NOT a real LC0 wear model.

Fresh tires start at100% of r17 grip. Targets: lap5=99.5%,10=98%,12=96%,14=93%,15=90%,16=80%,17=70%,18+=60%. Count uses completed laps since last service, including invalid laps; first partial outlap counts when crossing start/finish. The penalty changes smoothly over about a second, not as a sudden force step. Both lateral and longitudinal final tire-force multipliers change equally on all four wheels. This is an artificial force scaling layer, not calibrated tire friction physics; FFB feel can differ. It does not puncture tires or force a retirement.

New-set reset: native four-wheel virtual-km reset detected while stationary in your own pit box, OR10 uninterrupted seconds stationary below0.5km/h in your own pit box. The10-second option intentionally awards a new virtual set even if you only refuel/do not select physical tire service; it is the arcade pit rule. Merely driving down the pitlane or stopping beside the track does not reset. Leaving the box resets the timer. ESC teleport alone retains stint age, though new native tires or the10-second box stop can replenish it. A backwards session lap counter/new session resets. Reconnecting/reloading scripts can reset state; this is not server-authoritative anti-cheat.

All drivers must use the same r18 files and compatible CSP physics. Use tracks with working lap timing and pit-box detection. No promise of identical multiplayer/AI behavior until runtime tested; AI pit strategy is NOT automated. Ordinary tire-wear HUD does not represent this synthetic rule. Optional bundled SRT Tire Stint Lua app shows stint laps, force multiplier and pit timer. Enable/open it in the right-side app list; CSP0.2.11 required. If app data stays unavailable or no grip change occurs, report it instead of assuming the rule works.

Install full ZIP, or small patch only over r17, into Assetto Corsa root and overwrite; includes apps/lua/srt_tire_stint. Restart session. UI0.18.0. R17 brake light/collision candidate/12 skins and r16 setup controls retained. Only car physics script changes; tyres.ini, temperature/wear LUTs and handling defaults remain r17. Real-temperature lab experiments were shelved after user's clarified race-game objective. Fresh-set peak grip remains r17.

Rollback: restore r17 data/script.lua and ui/ui_car.json (or reinstall r17). Optional HUD can stay installed or be removed. Test one full stint and pit reset before using in an organized race; mock tests do not prove actual API force application, service timing, UI or multiplayer behavior.

Validation: executed composed Lua with mocked SDK for lap progression, equal per-wheel scaling,15/16/18-lap targets, floor, repeat samples, own-box10s timing, no pitlane/trackside reset, native tire reset, teleport retention, session decrease and launch-limiter regression; HUD Lua parsed/executed. Whole ZIP content verified. No runtime driving test performed. APIs from installed CSP0.2.11 Lua SDK: accessCarPhysics/wheels.finalForceMult,car.lapCount,isInPit,tyreVirtualKM,controllerInputs/getCarPhysics.scriptControllerInputs.
'''
(R/'RELEASE_NOTES.md').write_text(notes);ui=json.loads(raw[prefix+'ui/ui_car.json']);ui.update(version='0.18.0',description='r18 race-game tire rule: plan pit stops every15 completed laps. New set after actual4-tire reset or10seconds stationary in own pit box. Synthetic equal tire-force scaling; not real LC0 degradation. R17 features retained. CSP0.2.11 required. Runtime testing pending.')
over={prefix+'data/script.lua':script.encode(),prefix+'ui/ui_car.json':(json.dumps(ui,indent=2)+'\n').encode(),prefix+'RELEASE_r18.md':notes.encode(),'apps/lua/srt_tire_stint/manifest.ini':manifest.encode(),'apps/lua/srt_tire_stint/srt_tire_stint.lua':hud.encode()}
for name,b in over.items():f=R/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
D=R/'download';D.mkdir(exist_ok=True);archive=D/'SRT_2025-2026_r18_Assetto_Corsa.zip';hashes={};changed=[]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,b in raw.items():
  bb=over.get(name,b)
  if b!=bb:changed.append(name)
  z.writestr(name,bb);hashes[name]=hashlib.sha256(bb).hexdigest()
 for name,b in over.items():
  if name not in raw:z.writestr(name,b);hashes[name]=hashlib.sha256(b).hexdigest()
assert set(changed)=={prefix+'data/script.lua',prefix+'ui/ui_car.json'}
with zipfile.ZipFile(archive) as z:
 for name,digest in hashes.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
patch=D/'SRT_r17_to_r18_Test_Patch.zip'
with zipfile.ZipFile(patch,'w',zipfile.ZIP_DEFLATED) as z:
 for name,b in over.items():z.writestr(name,b)
checks={'lap_targets':{'0':1,'5':.995,'10':.98,'12':.96,'14':.93,'15':.90,'16':.80,'17':.70,'18':.60},'pit_box_service_seconds':10,'mock_lua_tests':'passed','launch_regression':'passed','hud_mock_execution':'passed','runtime_tested':False,'changed_existing_files':changed,'zip_verified':True};(R/'validation.json').write_text(json.dumps(checks,indent=2));(R/'file-manifest.json').write_text(json.dumps(hashes,indent=2));info={'version':'0.18.0','archive':str(archive.resolve()),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'zip_verified':True,'driver_validation':'pending'};(D/'package.json').write_text(json.dumps(info,indent=2));(D/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in [archive,patch]));print(json.dumps(checks,indent=2))
