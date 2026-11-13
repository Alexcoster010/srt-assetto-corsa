-- SRT r20: gameplay wear, not a calibrated physical tire model.
local previousUpdate, previousReset = script.update, script.reset
local ph = ac.accessCarPhysics()
local age, lastLap, serviceTime, serviced = 0, nil, 0, false
local oldVkm, changedWheels = {}, {}
local wear, grip = {}, {}
local function clamp(v,a,b) return math.max(a,math.min(b,v)) end
local function fresh()
  for i=0,3 do wear[i]=0;grip[i]=1 end
end
fresh()
local function newSet()
  fresh();age=0;serviceTime=0;serviced=true;changedWheels={}
end
function script.reset()
  if previousReset then previousReset() end
  serviceTime=0;serviced=false;changedWheels={}
  -- A teleport alone does not replenish tires.
end
function script.update(dt)
  if previousUpdate then previousUpdate(dt) end
  dt=clamp(dt or 0,0,.1)
  local lap=math.max(0,math.floor(car.lapCount or 0))
  if lastLap~=nil then
    if lap<lastLap then fresh();age=0;serviceTime=0;serviced=false;changedWheels={}
    elseif lap>lastLap then age=age+lap-lastLap end
  end
  lastLap=lap
  local speed=math.abs(car.speedKmh)
  local inBox=car.isInPit and speed<.5
  if inBox then
    for i=0,3 do
      local v=car.wheels[i].tyreVirtualKM
      if oldVkm[i] and oldVkm[i]>.000001 and v<oldVkm[i]*.5 then changedWheels[i]=true end
    end
    if not serviced then
      serviceTime=serviceTime+dt
      if (changedWheels[0] and changedWheels[1] and changedWheels[2] and changedWheels[3]) or serviceTime>=10 then newSet() end
    end
  else serviceTime=0;serviced=false;changedWheels={} end
  local length=ac.getSim().trackLengthM
  local validLength=length~=nil and length==length and length>50
  if not validLength then length=1000 end
  local distance=speed/3.6*dt
  local sum,minimum=0,1
  for i=0,3 do
    local w=car.wheels[i]
    oldVkm[i]=w.tyreVirtualKM
    -- Static axle loads for this build, overwritten by builder from car data.
    local referenceLoad=i<2 and 656.865756941650 or 718.986743058350
    local load=math.max(0,w.load or 0)
    local temp=w.tyreCoreTemperature or 60
    -- At 60C, static load and no excessive slip, 15 track lengths cost 30%.
    local thermal=clamp(1+.01*(temp-60),.75,1.8)
    local loading=clamp(load/referenceLoad,0,3)^1.2
    -- Absolute slip penalizes braking lockups and powered wheelspin alike.
    local sliding=1+3*clamp((math.abs(w.slipRatio or 0)-.15)/.85,0,1)
    if speed>5 and load>20 then
      wear[i]=math.min(.40,wear[i]+.02*(distance/length)*thermal*loading*sliding)
    end
    local target=1-wear[i]
    grip[i]=grip[i]+(target-grip[i])*(1-math.exp(-dt/.5))
    ph.wheels[i].finalForceMult.x=grip[i]
    ph.wheels[i].finalForceMult.y=grip[i]
    ph.controllerInputs[245+i]=grip[i]
    sum=sum+grip[i];minimum=math.min(minimum,grip[i])
  end
  ph.controllerInputs[240]=age
  ph.controllerInputs[241]=sum/4
  ph.controllerInputs[242]=serviceTime
  ph.controllerInputs[243]=20
  ph.controllerInputs[244]=serviced and 1 or 0
  ph.controllerInputs[249]=validLength and 1 or 0
  ph.controllerInputs[250]=minimum
end
