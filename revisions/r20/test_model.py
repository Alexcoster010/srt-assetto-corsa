import sys
sys.path.insert(0,str(P/'release-r16/test-tools'))
from lupa import LuaRuntime
def setup():
    lua=LuaRuntime()
    lua.execute('''script={}; car={index=0,lapCount=0,speedKmh=60,clutch=0,gear=2,isInPit=false,wheels={}}; ph={wheels={},controllerInputs={}}; sim={trackLengthM=1000}; ref={value=40}; for i=0,3 do car.wheels[i]={tyreVirtualKM=1,tyreCoreTemperature=60,load=280.5*9.81*(i<2 and .47742454728370215 or (1-.47742454728370215))/2,slipRatio=0}; ph.wheels[i]={finalForceMult={x=1,y=1}} end; ac={getSim=function() return sim end,accessCarPhysics=function() return ph end,getScriptSetupValue=function() return ref end,setEngineRPMLimit=function(v,s) limit=v end,setWingGain=function(i,cd,cl) end}''')
    lua.execute(script)
    return lua,lua.globals()
def step(g,seconds,dt=.05):
    for _ in range(round(seconds/dt)):g.script.update(dt)
def result(g):return [g.ph.controllerInputs[245+i] for i in range(4)]
lua,g=setup();step(g,900)
assert all(abs(x-.70)<.0003 for x in result(g)),result(g)
test_results={'nominal_15_track_lengths':result(g)}
for label,field,value in [('hot','tyreCoreTemperature',100),('high_load','load',1300),('lockup','slipRatio',-1),('wheelspin','slipRatio',1),('cool','tyreCoreTemperature',35)]:
    l,h=setup();setattr(h.car.wheels[0],field,value);step(h,300)
    r=result(h);assert r[0]>r[1] if label=='cool' else r[0]<r[1]
    assert max(r[1:])-min(r[1:])<1e-9
    test_results[label]=r
l,h=setup();h.car.wheels[0].load=0;step(h,100);assert result(h)[0]==1 and result(h)[1]<1
l,h=setup();h.car.speedKmh=0;step(h,100);assert result(h)==[1]*4
l,h=setup();h.sim.trackLengthM=0;step(h,60);assert h.ph.controllerInputs[249]==0 and abs(result(h)[0]-.98)<.0003
l,h=setup();step(h,900,.02);assert abs(result(h)[0]-result(g)[0])<.00002
step(g,1000);assert all(abs(x-.60)<1e-8 for x in result(g))
g.car.lapCount=15;g.car.speedKmh=0;step(g,1);g.script.reset();step(g,12)
assert g.ph.controllerInputs[240]==15 and result(g)[0]<.601
g.car.isInPit=True;step(g,9);assert result(g)[0]<.601
g.car.isInPit=False;step(g,1);g.car.isInPit=True;step(g,9);assert result(g)[0]<.601
step(g,1.1);assert result(g)==[1]*4 and g.ph.controllerInputs[240]==0
g.car.isInPit=False;g.car.speedKmh=60;g.car.lapCount=20;step(g,60)
assert g.ph.controllerInputs[240]==5 and result(g)[0]<1
g.car.isInPit=True;g.car.speedKmh=0
for i in range(4):g.car.wheels[i].tyreVirtualKM=0
step(g,.05);assert result(g)==[1]*4
g.car.isInPit=False;g.car.speedKmh=60;step(g,60);g.car.lapCount=0;g.car.speedKmh=0;step(g,.05)
assert result(g)==[1]*4 and g.ph.controllerInputs[240]==0
g.car.gear=2;g.car.clutch=1;g.script.reset();step(g,.05);assert g.limit==8000
g.car.clutch=0;step(g,.05);assert g.limit==16000
for i in range(4):assert g.ph.wheels[i].finalForceMult.x==g.ph.wheels[i].finalForceMult.y
test_results['service_reset_floor_timestep_launch']='passed'
