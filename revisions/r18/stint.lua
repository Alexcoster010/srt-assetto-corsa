-- SRT r18: deliberate race-game tire life, not an LC0 degradation model.
local previousUpdate = script.update
local previousReset = script.reset
local ph = ac.accessCarPhysics()
local age, lastLap, grip, serviceTime, serviced = 0, nil, 1, 0, false
local oldVkm = {}
local changedWheels = {}
local knots = {{0,1},{5,.995},{10,.98},{12,.96},{14,.93},{15,.90},{16,.80},{17,.70},{18,.60}}
local function targetGrip(laps)
  for i=2,#knots do
    local a,b=knots[i-1],knots[i]
    if laps<=b[1] then return a[2]+(b[2]-a[2])*(laps-a[1])/(b[1]-a[1]) end
  end
  return .60
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
  ph.controllerInputs[243]=18
  ph.controllerInputs[244]=serviced and 1 or 0
end
