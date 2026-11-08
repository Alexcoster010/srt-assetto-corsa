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
