from pathlib import Path
import configparser as cp,json,os,shutil,math,hashlib
P=Path(os.environ.get('SRT_AC_PROJECT',str(Path(__file__).resolve().parents[1])));R=P/'release-r07';O=R/'content/cars/srt27_prototype';D=O/'data'
def edit(n,sections):
 c=cp.ConfigParser(strict=False,inline_comment_prefixes=(';',));c.optionxform=str;c.read(D/n)
 for k,v in sections.items():
  if k not in c:c[k]={}
  c[k].update({a:str(b) for a,b in v.items()})
 with (D/n).open('w') as f:c.write(f,space_around_delimiters=False)
edit('engine.ini',{'ENGINE_DATA':{'INERTIA':.12}})
# Gain normalization is a provisional test setting; it cannot repair disabled device feedback.
edit('car.ini',{'CONTROLS':{'FFMULT':2.5,'STEER_ASSIST':1.0}})
edit('setup.ini',{'FRONT_BIAS':{'SHOW_CLICKS':0,'TAB':'GENERIC','NAME':'Brake bias - front percent','MIN':60,'MAX':85,'STEP':.5,'POS_X':.5,'POS_Y':1,'HELP':'HELP_BRAKE_BIAS'}})
s='; Original SRT simulator dashboard. No CSP or wheel-specific software required.\n[DISPLAY_0]\nNAME=SRT_DASH_SCREEN\nEMISSIVE=1.8,2.1,1.6\nINTENSITY=1.0\n\n'
for i,typ,pos,size,font in [(0,'GEAR','0.052,-0.012,-0.0125',.043,'e92_big'),(1,'RPM','-0.028,0.009,-0.0125',.015,'e92_mid'),(2,'SPEED','-0.028,-0.020,-0.0125',.017,'e92_mid')]:
 s+=f'[ITEM_{i}]\nPARENT=SRT_DASH\nPOSITION={pos}\nTYPE={typ}\nSIZE={size}\nCOLOR=8,12,8,255\nINTENSITY=1\nFONT={font}\nVERSION=2\nALIGN=CENTER\n'+('UNITS=SYSTEM\n' if typ=='SPEED' else '')+'\n'
for i in range(8):
 color='0,40,0' if i<4 else ('40,25,0' if i<6 else '50,0,0')
 s+=f'[LED_{i}]\nOBJECT_NAME=SRT_SHIFT_{i}\nRPM_SWITCH={11000+500*i}\nEMISSIVE={color}\nDIFFUSE=0.3\nBLINK_SWITCH=14500\nBLINK_HZ=5\n\n'
(D/'digital_instruments.ini').write_text(s)
# Effective axle loads, not isolated wing predictions. Rear/body CFD is used as one force anchor.
wb=1.6637;front_weight=.47742454728370215;front_z=wb*(1-front_weight);rear_z=-wb*front_weight
s='; r07 PRELIMINARY: effective CL*A=2.60 m2, CD*A=1.00 m2, 40% front load.\n; Equivalent forces at axles; no validated pitch/ride-height/yaw map. See DRIVER_FEEDBACK.md.\n[HEADER]\nVERSION=3\n\n'
for i,(name,cl,cd,z) in enumerate([('SRT_FRONT_EQUIVALENT',1.04,.4,front_z),('SRT_REAR_EQUIVALENT',1.56,.6,rear_z)]):
 clfile='srt_aero_'+str(i)+'_cl.lut';cdfile='srt_aero_'+str(i)+'_cd.lut'
 # Mild bounded angle response; broad end points avoid extrapolation beyond authored data.
 (D/clfile).write_text('\n'.join(str(a)+'|'+str(round(cl*math.cos(math.radians(a))**2,8)) for a in [-180,-90,-45,-20,0,20,45,90,180])+'\n')
 (D/cdfile).write_text('\n'.join(str(a)+'|'+str(round(cd*(1+math.sin(math.radians(a))**2),8)) for a in [-180,-90,-45,-20,0,20,45,90,180])+'\n')
 s+=f'[WING_{i}]\nNAME={name}\nCHORD=1\nSPAN=1\nPOSITION=0,0,{z}\nLUT_AOA_CL={clfile}\nLUT_GH_CL=\nCL_GAIN=1\nLUT_AOA_CD={cdfile}\nLUT_GH_CD=\nCD_GAIN=1\nANGLE=0\n'
 for zone in ['FRONT','REAR','LEFT','RIGHT']:
  s+=f'ZONE_{zone}_CL=0\nZONE_{zone}_CD=0\n'
 s+='YAW_CL_GAIN=0\n\n'
(D/'aero.ini').write_text(s)
mad=Path(os.environ.get('SRT_MAD_CAR',str(Path(os.environ['TEMP'])/'srt-mad-mft02-v142/content/cars/madformulateam_mft02')))
shutil.copy2(mad/'sfx/madformulateam_mft02.bank',O/'sfx/srt27_prototype.bank');(O/'sfx/GUIDs.txt').write_text((mad/'sfx/GUIDs.txt').read_text().replace('madformulateam_mft02','srt27_prototype'))
ui=json.loads((O/'ui/ui_car.json').read_text());ui['version']='0.7';ui['description']='SRT 2025-2026 No.31, native team CAD with 18 x 6 inch tires. r07 driver-feedback prototype: gear/RPM/speed dash, shift lights, increased engine inertia, MAD high-rev reference sound, preliminary CFD-anchored aero and adjustable brake bias. FFB gain is provisional and wheel-independent. Handling, cockpit readability, sound character and Sazuka FS grass require driver validation.';(O/'ui/ui_car.json').write_text(json.dumps(ui,indent=2))
(O/'LOCAL_ASSET_PROVENANCE.txt').write_text('Original team CAD vehicle geometry and procedural livery/dashboard. Photo-derived sidepod shells. Temporary MAD Formula MFT02 engine sound and driver pose/animations; Kunos driver/ancillary dependencies. Sound is a high-RPM reference, not a measured recording of the SRT Kawasaki 636. This build does not grant rights to third-party source assets.\n')
g=cp.ConfigParser();g.read(D/'drivetrain.ini');fd=float(g['GEARS']['FINAL']);gears=[float(g['GEARS']['GEAR_'+str(i)]) for i in range(1,7)]
report={'inertia_kg_m2':{'r06':.08,'r07':.12,'status':'user-requested tuning candidate; not measured','free_acceleration_ratio_same_torque':.08/.12},'gear_speeds_at_14500_kmh':[14500/(fd*x)*math.pi*.4572*60/1000 for x in gears],'aero':{'status':'preliminary assumed full-car closure, partial CFD force anchor only','CL_area_m2':2.6,'CD_area_m2':1.,'front_fraction':.4,'density_kg_m3':1.225,'rows':[{'speed_kmh':v,'downforce_N':.5*1.225*(v/3.6)**2*2.6,'drag_N':.5*1.225*(v/3.6)**2} for v in [48.28032,60,80,100,120]],'rear_anchor':{'iteration':'GEB-RW-1.2*','speed_mph':30,'downforce_raw':38.58,'drag_raw':23.88,'units':'lbf inferred from template; requires team confirmation','description':'starred configuration; rear/body interpretation inferred from earlier starred row, not whole-car CFD'}},'brakes':{'max_torque_parameter_Nm':571,'front_bias_default':.75,'front_per_wheel_assumed_Nm':428.25,'rear_per_wheel_assumed_Nm':142.75,'bias_setup_percent':[60,85],'torque_changed':False},'ffb':{'gain_r06':1,'gain_r07':2.5,'steer_assist':1,'status':'normalization candidate, not a verified zero-FFB fix','device_specific_settings':False},'track':'Sazuka FS not installed; surface diagnosis pending exact track'}
(R/'physics-review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))


report_path=R/"build-report.json"
build=json.loads(report_path.read_text());build["final_physics_sha256"]={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ["engine.ini","power.lut","drivetrain.ini","suspensions.ini","tyres.ini","brakes.ini","aero.ini","car.ini","setup.ini","digital_instruments.ini"]};build["runtime_test"]="See runtime-status.json for separate observed test; regeneration alone is not a runtime pass";build["limits"][-1]="Visual suspension linkages remain static. Driver pose and MAD reference audio remain provisional.";report_path.write_text(json.dumps(build,indent=2))
