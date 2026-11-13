function script.windowMain(dt)
  local p=ac.getCarPhysics(0)
  if p==nil or p.scriptControllerInputs[243]~=20 then
    ui.text('SRT r20 tire wear data unavailable');return
  end
  local d=p.scriptControllerInputs
  ui.text(string.format('Stint: %d laps | Mean grip: %.1f%%',d[240],100*d[241]))
  ui.text(string.format('FL %.1f%%   FR %.1f%%',100*d[245],100*d[246]))
  ui.text(string.format('RL %.1f%%   RR %.1f%%',100*d[247],100*d[248]))
  if d[249]<1 then ui.text('No track length: using 1000 m baseline') end
  if d[244]>0 then ui.text('New set ready')
  elseif d[242]>0 then ui.text(string.format('Pit service: %.1f / 10 seconds',d[242]))
  elseif d[250]<=.701 then ui.text('Tire at 70% or less: pit recommended') end
end
