import configparser,io,re,math,csv
source=P.parent/'tire-compound-refit-2026-10-01/R20_18x6_rim6/R20_18x6_rim6_refit.tir'
values={}
for line in source.read_text().splitlines():
    m=re.match(r'^([A-Z0-9_]+)\s*=\s*([-+0-9.eE]+)\s*$',line)
    if m:values[m[1]]=float(m[2])
samples=[[float(v) for v in row] for row in csv.reader((R/'r20-force-samples.csv').open())]
assert len(samples)==8 and all(all(math.isfinite(x) for x in row) for row in samples)
cfg=configparser.ConfigParser(interpolation=None,strict=True);cfg.optionxform=str
cfg.read_string(raw[prefix+'data/tyres.ini'].decode())
assert cfg['COMPOUND_DEFAULT']['INDEX']=='0'
original={sec:dict(cfg[sec]) for sec in ['HEADER','COMPOUND_DEFAULT','FRONT','REAR','THERMAL_FRONT','THERMAL_REAR']}
conversion={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'method':'MF6.1 force sweeps at12psi,zero camber; bounded-envelope projection into AC v7 parameters',
 'valid_range_N':[150,1250],'angle_range_deg':[-12,12],'long_slip_range':[-.2,.2],
 'peak_caveat':'Maximum sampled forces occur at the slip range edges; these are bounded-envelope maxima, not confirmed physical peaks.',
 'unknowns_retained_from_LC0':['vertical stiffness/damping','relaxation length','camber coefficients','thermal model','rolling resistance','combined-slip shape','aligning torque representation'],
 'startup_correction':'Restore KEY=value syntax; no spaces adjacent to equals; runtime confirmation pending',
 'axles':{}}
for axle in ['FRONT','REAR']:
    sec=axle+'_1';c=cfg[sec];fz=float(cfg[axle]['FZ0'])
    # Interpolate only within measured-domain samples; fit local load exponent.
    def interp(load,col):
        for a,b in zip(samples,samples[1:]):
            if a[0]<=load<=b[0]:return a[col]+(b[col]-a[col])*(load-a[0])/(b[0]-a[0])
        raise ValueError('load outside sampled envelope')
    def exponent(col):return math.log(interp(fz*1.1,col)/interp(fz*.9,col))/math.log(1.1/.9)
    changes={'NAME':'R20 fitted 18x6','SHORT_NAME':'R20','WIDTH':values['WIDTH'],
      'RADIUS':values['UNLOADED_RADIUS'],'RIM_RADIUS':values['RIM_RADIUS'],
      'DX_REF':interp(fz,1)/fz,'DY_REF':interp(fz,2)/fz,
      'DX0':interp(fz,1)/fz,'DY0':interp(fz,2)/fz,
      'LS_EXPX':exponent(1),'LS_EXPY':exponent(2),
      'FRICTION_LIMIT_ANGLE':interp(fz,4)}
    for key,value in changes.items():c[key]=str(value) if isinstance(value,str) else format(value,'.12g')
    assert 0<float(c['RIM_RADIUS'])<float(c['RADIUS']) and float(c['RATE'])>0
    assert .3<float(c['LS_EXPX'])<1.2 and .3<float(c['LS_EXPY'])<1.2
    conversion['axles'][axle]={'FZ0':fz,'parameters':changes,'cornering_stiffness_N_per_rad':interp(fz,5),
      'sampled_peak_slip_ratio':interp(fz,3),'native_cornering_stiffness_mapping':'not exact; AC v7 friction-angle approximation'}
    for col,exp,ref in [(1,float(c['LS_EXPX']),float(c['DX_REF'])),(2,float(c['LS_EXPY']),float(c['DY_REF']))]:
        errs=[abs(ref*fz*(row[0]/fz)**exp/row[col]-1) for row in samples if 400<=row[0]<=1000]
        assert max(errs)<.1,errs
        conversion['axles'][axle]['longitudinal' if col==1 else 'lateral']={'load_projection_max_relative_error_400_1000N':max(errs)}
for sec,before in original.items():assert dict(cfg[sec])==before,'LC0/default changed'
buf=io.StringIO();cfg.write(buf,space_around_delimiters=False)
tyres=buf.getvalue()
for line in tyres.splitlines():
    if '=' in line:
        key,value=line.split('=',1);assert key==key.strip() and value==value.strip()
assert 'NAME=LC0 approximation' in tyres and 'NAME=R20 fitted 18x6' in tyres
assert len([s for s in cfg.sections() if s=='FRONT' or s.startswith('FRONT_')])==2
for sec in ['FRONT','REAR','FRONT_1','REAR_1']:
    assert prefix+'data/'+cfg[sec]['WEAR_CURVE'] in raw
for sec in ['THERMAL_FRONT','THERMAL_REAR','THERMAL_FRONT_1','THERMAL_REAR_1']:
    assert prefix+'data/'+cfg[sec]['PERFORMANCE_CURVE'] in raw
over[prefix+'data/tyres.ini']=tyres.encode('ascii')
(R/'conversion.json').write_text(json.dumps(conversion,indent=2))
