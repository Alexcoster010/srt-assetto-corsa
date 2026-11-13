function script.windowMain(dt)
  local p=ac.getCarPhysics(0)
  if p==nil or p.scriptControllerInputs[243]~=18 then
    ui.text('SRT r18 tire-stint data unavailable')
    return
  end
  local d=p.scriptControllerInputs
  ui.text(string.format('Tire stint: %d / 15 laps',d[240]))
  ui.text(string.format('Game-rule grip: %.1f%%',d[241]*100))
  if d[244]>0 then ui.text('New set ready')
  elseif d[242]>0 then ui.text(string.format('Pit service: %.1f / 10 seconds',d[242]))
  elseif d[240]>=15 then ui.text('PIT FOR A NEW SET')
  elseif d[240]>=13 then ui.text('Pit stop approaching') end
end
