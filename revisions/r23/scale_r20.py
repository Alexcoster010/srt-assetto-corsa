import configparser,io,math
cfg=configparser.ConfigParser(interpolation=None,strict=True);cfg.optionxform=str
cfg.read_string(raw[prefix+'data/tyres.ini'].decode())
before={s:dict(cfg[s]) for s in cfg.sections()}
conversion={'targets_g':{'lateral':1.8,'acceleration':1.04,'braking':1.2},
 'method':'Match tuned LC0 lateral and longitudinal grip at each axle FZ0; retain R20 load exponents and friction angle',
 'runtime_targets_verified':False,
 'limits':'Reference-load normalization, not a hard G cap. Load transfer, aero, power and slip behavior affect actual maxima. Acceleration and braking share DX; separate exact limits cannot be enforced by these coefficients.',
 'axles':{}}
for axle in ['FRONT','REAR']:
    sec=axle+'_1';row={}
    for axis in ['X','Y']:
        key='D'+axis+'_REF';old=float(cfg[sec][key]);target=float(cfg[axle][key]);scale=target/old
        for k in [key,'D'+axis+'0']:cfg[sec][k]=cfg[axle][k]
        row[axis]={'r22_reference_grip':old,'r23_reference_grip':target,'multiplier':scale}
        assert 0<scale<1
        # Verify a constant force scaling over load while preserving the exponent.
        exp=float(cfg[sec]['LS_EXP'+axis]);fz=float(cfg[sec]['FZ0'])
        for load in [200,400,600,800,1000,1200]:
            old_force=old*fz*(load/fz)**exp;new_force=target*fz*(load/fz)**exp
            assert math.isclose(new_force/old_force,scale,rel_tol=1e-12)
    conversion['axles'][axle]=row
allowed={'DX_REF','DX0','DY_REF','DY0'}
for sec,old in before.items():
    changes={k for k in old if cfg[sec][k]!=old[k]}
    assert changes==(allowed if sec in ['FRONT_1','REAR_1'] else set()),(sec,changes)
buf=io.StringIO();cfg.write(buf,space_around_delimiters=False)
for line in buf.getvalue().splitlines():
    if '=' in line:
        k,v=line.split('=',1);assert k==k.strip() and v==v.strip()
over[prefix+'data/tyres.ini']=buf.getvalue().encode('ascii')
(R/'conversion.json').write_text(json.dumps(conversion,indent=2))
