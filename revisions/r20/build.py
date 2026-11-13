from pathlib import Path
import zipfile,json,hashlib,sys
R=Path(__file__).resolve().parent;P=R.parent;prefix='content/cars/srt27_prototype/';base=R/'baseline-r19.zip'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='4a7c0b44894c08bde1d7fb0cb3abcba5272e2571242e1827b7c73f9078517983'
with zipfile.ZipFile(base) as z:raw={n:z.read(n) for n in z.namelist()}
script=raw[prefix+'data/script.lua'].decode().split('-- SRT r19: deliberate race-game tire life')[0].rstrip()+'\n\n'+(R/'stint.lua').read_text()
exec((R/'test_model.py').read_text())
hud=(R/'hud.lua').read_text()
manifest='[ABOUT]\nNAME=SRT Tire Stint\nAUTHOR=SRT project\nVERSION=0.20.0\nDESCRIPTION=15-lap tire-stint counter and pit service timer\n\n[WINDOW_0]\nID=main\nNAME=SRT Tire Stint\nFUNCTION_MAIN=windowMain\nSIZE=300,140\n'
# Parse Lua HUD too, with a test UI and state.
lua.execute('ui={text=function(x) end}; ac.getCarPhysics=function(i) return {scriptControllerInputs=ph.controllerInputs} end');lua.execute(hud);g.script.windowMain(.02)
notes=(R/'RELEASE_NOTES.md').read_text()
(R/'RELEASE_NOTES.md').write_text(notes);ui=json.loads(raw[prefix+'ui/ui_car.json']);ui.update(version='0.20.0',description='r20 per-tire gameplay wear: temperature, normal load and slip affect continuous wear. Nominal 70% grip after 15 track lengths, 60% floor. Pit reset unchanged. Optional per-tire HUD. CSP0.2.11 required; runtime validation pending.')
over={prefix+'data/script.lua':script.encode(),prefix+'ui/ui_car.json':(json.dumps(ui,indent=2)+'\n').encode(),prefix+'RELEASE_r20.md':notes.encode(),'apps/lua/srt_tire_stint/manifest.ini':manifest.encode(),'apps/lua/srt_tire_stint/srt_tire_stint.lua':hud.encode()}
for name,b in over.items():f=R/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
D=R/'download';D.mkdir(exist_ok=True);archive=D/'SRT_2025-2026_r20_Assetto_Corsa.zip';hashes={};changed=[]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,b in raw.items():
  bb=over.get(name,b)
  if b!=bb:changed.append(name)
  z.writestr(name,bb);hashes[name]=hashlib.sha256(bb).hexdigest()
 for name,b in over.items():
  if name not in raw:z.writestr(name,b);hashes[name]=hashlib.sha256(b).hexdigest()
assert set(changed)=={prefix+'data/script.lua',prefix+'ui/ui_car.json','apps/lua/srt_tire_stint/manifest.ini','apps/lua/srt_tire_stint/srt_tire_stint.lua'}
with zipfile.ZipFile(archive) as z:
 for name,digest in hashes.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
patch=D/'SRT_r19_to_r20_Test_Patch.zip'
with zipfile.ZipFile(patch,'w',zipfile.ZIP_DEFLATED) as z:
 for name,b in over.items():z.writestr(name,b)
checks={'model_tests':test_results,'pit_box_service_seconds':10,'mock_lua_tests':'passed','launch_regression':'passed','hud_mock_execution':'passed','runtime_tested':False,'changed_existing_files':changed,'zip_verified':True};(R/'validation.json').write_text(json.dumps(checks,indent=2));(R/'file-manifest.json').write_text(json.dumps(hashes,indent=2));info={'version':'0.20.0','archive':str(archive.resolve()),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'zip_verified':True,'driver_validation':'pending'};(D/'package.json').write_text(json.dumps(info,indent=2));(D/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in [archive,patch]));print(json.dumps(checks,indent=2))
