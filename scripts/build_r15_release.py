from pathlib import Path
import json,zipfile,hashlib,configparser
import numpy as np

P=Path(__file__).resolve().parents[1];R=P/'release-r15';D=R/'download';D.mkdir(exist_ok=True);prefix='content/cars/srt27_prototype/'
baseline=R/'baseline-r14.zip';assert hashlib.sha256(baseline.read_bytes()).hexdigest()==json.loads((P/'release-r14/download/published.json').read_text())['sha256']
with zipfile.ZipFile(baseline) as z:
 power=z.read(prefix+'data/power.lut').decode();drive=z.read(prefix+'data/drivetrain.ini').decode();ui=json.loads(z.read(prefix+'ui/ui_car.json'))
a=np.array([[float(v) for v in l.split('|')] for l in power.splitlines() if '|' in l]);peak=float(a[np.argmax(a[:,1]),0]);target=peak-1000
# Preserve all original breakpoints as well as the exact translated interpolation knots.
warped=np.interp(a[:,0],[0,2500,peak,16000],[0,2500,target,16000]);x=np.unique(np.r_[a[:,0],warped,np.arange(2500,16001,50),target]);old=np.interp(x,*a.T)
mapped=np.interp(x,[0,2500,target,16000],[0,2500,peak,16000]);base=np.interp(mapped,*a.T)
bump=.04*old*np.sin(np.pi*np.clip((x-2500)/6500,0,1))**2
w=np.clip((x-target)/(16000-target),0,1);comp=np.trapezoid(base+bump-old,x)/np.trapezoid(w,x);new=base+bump-comp*w
lut=''.join(f'{rpm:.9f}|{torque:.12f}\n' for rpm,torque in zip(x,new))
arr=np.array([[float(v) for v in l.split('|')] for l in lut.splitlines()]);assert abs(np.trapezoid(arr[:,1],arr[:,0])-np.trapezoid(a[:,1],a[:,0]))<1e-5;assert arr[np.argmax(arr[:,1]),0]==target;assert new.min()>=0
# Use documented SDK autoclutch section references and milliseconds.
drive=drive.replace('CHANGE_UP_TIME=80','CHANGE_UP_TIME=100').replace('AUTO_CUTOFF_TIME=80','AUTO_CUTOFF_TIME=100').replace('UPSHIFT_PROFILE=NONE','UPSHIFT_PROFILE=SRT_UPSHIFT').replace('GAS_CUTOFF_TIME=0.08','GAS_CUTOFF_TIME=0.10')
drive+='\n[SRT_UPSHIFT]\nPOINT_0=10\nPOINT_1=100\nPOINT_2=180\n'
cp=configparser.ConfigParser();cp.read_string(drive);assert cp['AUTOCLUTCH']['UPSHIFT_PROFILE'] in cp;assert cp.getint('SRT_UPSHIFT','POINT_0')<cp.getint('SRT_UPSHIFT','POINT_1')<cp.getint('SRT_UPSHIFT','POINT_2')
ui.update(version='0.15.0',description='r15 test: torque peak moved from13250 to12250rpm, increased low/mid torque and reduced upper-end torque with unchanged RPM-integrated average. Upshift100ms cut/shift with clutch re-engagement100-180ms. Retains r14 softer rear and nominal9in CG. Inertia0.03 unchanged. Driver validation pending. CSP0.2.11 required.')
notes=f'''# SRT r15 â€” torque curve and upshift feel test

Built November 7, 2026 from checksum-verified public r14.

- Peak torque moves {peak:.0f} -> {target:.0f} RPM, keeping peak{new.max():.6f}Nm.
- Smooth low/mid-RPM increase, compensated with greater upper-end drop-off. Average torque is preserved as the trapezoidal area under the piecewise-linear torque-vs-RPM LUT divided by the RPM span, not the unweighted average of unequal-spaced samples. Full0-16000rpm and operating1400-16000rpm integrals preserved because0-2500rpm remains unchanged. This does not preserve power, shift-optimal RPM, or acceleration time.
- Upshift duration80 ->100ms, automatic torque cut80 ->100ms; autoclutch reaches disengaged at10ms, starts engagement100ms, finishes180ms. AI cutoff0.08 ->0.10s. USE_ON_CHANGES=1 retained. Synthetic clutch profile is a shift-feel approximation, not a claim of the real car's clutch actuation. No measured torque-return trace is available.
- Engine inertia0.03, clutch capacity100Nm, downshift timing/autoblip, rev limiter16000, auto-shift threshold14500rpm, differential and all handling settings remain unchanged. Retains r14 rear springs30% softer and prior nominal9in CG.

Install: back up your existing srt27_prototype folder, extract the full ZIP into the Assetto Corsa root and overwrite. Restart session; Content Manager should show0.15.0. Requires CSP0.2.11. The small patch ZIP is for r14 only. Reinstall r14 for rollback.

Validation: exact serialized LUT integration, peak location, positivity, profile ordering, changed-file allowlist and full package hashes checked. No runtime/driver test performed. Test moderate then full-throttle upshifts across gears for kick, RPM flare/bog, and clutch slip. Report shift RPM and gear pair. The changed torque curve can change the best shift point;14500rpm automatic threshold is retained pending testing. Do not treat this curve as measured dyno data.

Local primary parameter reference: installed Kunos SDK dev/content/cars/formula_k/data/drivetrain.ini, gearbox and autoclutch comments. Baseline and result hashes, torque samples and plots accompany the source revision.
'''
(R/'RELEASE_NOTES.md').write_text(notes,encoding='utf-8');(R/'power-r14.lut').write_text(power);(R/'power-r15.lut').write_text(lut)
overrides={'data/power.lut':lut.encode(),'data/drivetrain.ini':drive.encode(),'ui/ui_car.json':(json.dumps(ui,indent=2)+'\n').encode(),'RELEASE_r15.md':notes.encode()}
for name,b in overrides.items():
 f=R/'content/cars/srt27_prototype'/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
archive=D/'SRT_2025-2026_r15_Assetto_Corsa.zip';manifest={};changed=[]
with zipfile.ZipFile(baseline) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as dst:
 for name in src.namelist():
  raw=src.read(name);rel=name.removeprefix(prefix);b=overrides.get(rel,raw)
  if b!=raw:changed.append(rel)
  dst.writestr(name,b);manifest[name]=hashlib.sha256(b).hexdigest()
 dst.writestr(prefix+'RELEASE_r15.md',overrides['RELEASE_r15.md']);manifest[prefix+'RELEASE_r15.md']=hashlib.sha256(overrides['RELEASE_r15.md']).hexdigest()
assert set(changed)=={'data/power.lut','data/drivetrain.ini','ui/ui_car.json'}
with zipfile.ZipFile(archive) as z:
 for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
patch=D/'SRT_r14_to_r15_Test_Patch.zip'
with zipfile.ZipFile(patch,'w',zipfile.ZIP_DEFLATED) as z:
 for name,b in overrides.items():z.writestr(prefix+name,b)
checks={'peak_rpm_before':peak,'peak_rpm_after':target,'peak_torque_Nm':float(new.max()),'average_torque_0_16000_before':float(np.trapezoid(a[:,1],a[:,0])/16000),'average_torque_0_16000_after':float(np.trapezoid(arr[:,1],arr[:,0])/16000),'average_torque_1400_16000_before':float(np.trapezoid(a[a[:,0]>=1400,1],a[a[:,0]>=1400,0])/14600),'average_torque_1400_16000_after':float(np.trapezoid(arr[arr[:,0]>=1400,1],arr[arr[:,0]>=1400,0])/14600),'changed_existing_files':changed,'samples':[{'rpm':r,'r14_Nm':float(np.interp(r,x,old)),'r15_Nm':float(np.interp(r,x,new))} for r in [2500,4000,6000,8000,10000,12250,13250,14500,16000]],'runtime_validation':'not run','zip_content_verified':True}
(R/'validation.json').write_text(json.dumps(checks,indent=2));(R/'file-manifest.json').write_text(json.dumps(manifest,indent=2))
info={'version':'0.15.0','archive':str(archive.resolve()),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'zip_verified':True,'driver_validation':'pending'};(D/'package.json').write_text(json.dumps(info,indent=2))
def xy(r,t):return (65+(r-1400)/14600*790,395-t/40*330)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="480" viewBox="0 0 900 480"><rect width="900" height="480" fill="white"/><g font-family="Arial" fill="#222"><text x="65" y="30" font-size="19">SRT r15: earlier peak, unchanged average torque</text>']
for t in range(0,41,5):
 yy=xy(1400,t)[1];svg.append(f'<path d="M65 {yy} H855" stroke="#ddd"/><text x="50" y="{yy+4}" text-anchor="end">{t}</text>')
for r in range(2000,16001,2000):
 xx=xy(r,0)[0];svg.append(f'<text x="{xx}" y="418" text-anchor="middle">{r}</text>')
for values,color in [(a,'#667085'),(np.column_stack([x,new]),'#bf2633')]:
 pts=' '.join(f'{xy(r,t)[0]:.3f},{xy(r,t)[1]:.3f}' for r,t in values if r>=1400);svg.append(f'<polyline points="{pts}" stroke="{color}" stroke-width="2.5" fill="none"/>')
svg.append('<text x="65" y="53">Torque (Nm)</text><text x="660" y="53" fill="#667085">r14 baseline</text><text x="770" y="53" fill="#bf2633">r15 test</text><text x="460" y="450" text-anchor="middle">Engine speed (RPM)</text></g></svg>');(R/'torque-comparison.svg').write_text(''.join(svg))
(D/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in [archive,patch]))
print(json.dumps(checks,indent=2))
