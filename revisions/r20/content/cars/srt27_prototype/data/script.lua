-- SRT launch limiter; requires CSP 0.2.11 and extended car physics.
-- No engine torque, clutch, gearing, traction or inertia override.
local NORMAL_RPM = 16000
local LAUNCH_RPM = 8000
local active = false
local launched = false
local stationary = 0
local lastLimit = nil

local function applyLimit(value)
  if lastLimit ~= value then
    ac.setEngineRPMLimit(value, false)
    lastLimit = value
  end
end

function script.reset()
  active = false
  launched = false
  stationary = 0
  lastLimit = nil
  applyLimit(NORMAL_RPM)
end

function script.update(dt)
  -- SDK car.clutch: 1 means pedal fully depressed (clutch disconnected).
  local stopped = math.abs(car.speedKmh) < 0.5
  stationary = stopped and (stationary + dt) or 0
  if launched and stationary > 1 and car.clutch > 0.95 then
    launched = false
  end
  if active and (car.clutch < 0.80 or car.gear ~= 2 or not stopped) then
    active = false
    launched = true
  end
  if not launched and stopped and car.gear == 2 and car.clutch > 0.95 then
    active = true
  end
  applyLimit(active and LAUNCH_RPM or NORMAL_RPM)
end

-- SRT r16: one pit-setup slider redistributes existing wing lift.
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
