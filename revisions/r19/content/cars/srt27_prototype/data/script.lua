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

-- SRT r19: deliberate race-game tire life, not an LC0 degradation model.
local previousUpdate = script.update
local previousReset = script.reset
local ph = ac.accessCarPhysics()
local age, lastLap, grip, serviceTime, serviced = 0, nil, 1, 0, false
local oldVkm = {}
local changedWheels = {}
local function targetGrip(laps)
  return math.max(.60, 1 - .02 * math.max(0, laps))
end
local function newSet()
  age=0; serviceTime=0; serviced=true
  changedWheels={}
end
function script.reset()
  if previousReset then previousReset() end
  serviceTime=0; serviced=false; changedWheels={}
  -- Teleport/reset alone does not grant a fresh game-rule tire set.
end
function script.update(dt)
  if previousUpdate then previousUpdate(dt) end
  dt=math.max(0,math.min(dt or 0,.1))
  local lap=math.max(0,math.floor(car.lapCount or 0))
  if lastLap~=nil then
    if lap<lastLap then age=0;grip=1;serviceTime=0;serviced=false;changedWheels={}
    elseif lap>lastLap then age=age+(lap-lastLap) end
  end
  lastLap=lap
  local inBox=car.isInPit and math.abs(car.speedKmh)<.5
  if inBox then
    for i=0,3 do
      local v=car.wheels[i].tyreVirtualKM
      if oldVkm[i] and oldVkm[i]>.000001 and v<oldVkm[i]*.5 then changedWheels[i]=true end
    end
    if not serviced then
      serviceTime=serviceTime+dt
      if (changedWheels[0] and changedWheels[1] and changedWheels[2] and changedWheels[3]) or serviceTime>=10 then newSet() end
    end
  else
    serviceTime=0;serviced=false;changedWheels={}
  end
  for i=0,3 do oldVkm[i]=car.wheels[i].tyreVirtualKM end
  local target=targetGrip(age)
  grip=grip+(target-grip)*(1-math.exp(-dt/.5))
  for i=0,3 do
    ph.wheels[i].finalForceMult.x=grip
    ph.wheels[i].finalForceMult.y=grip
  end
  ph.controllerInputs[240]=age
  ph.controllerInputs[241]=grip
  ph.controllerInputs[242]=serviceTime
  ph.controllerInputs[243]=19
  ph.controllerInputs[244]=serviced and 1 or 0
end
