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
