"""SRT acceleration HUD. Reads telemetry only; no throttle or clutch control."""
import ac,acsys,os,json,time,sys,mmap,struct
sys.path.insert(0,os.path.dirname(__file__))
from timer_core import RunTimer
runner=RunTimer();label=None;saved=False;graphics=None

def reset(*args):
    global saved
    runner.reset();saved=False

def acMain(version):
    global label,graphics
    app=ac.newApp('SRT Acceleration');ac.setSize(app,410,180)
    label=ac.addLabel(app,'Stage behind GREEN start line');ac.setPosition(label,12,32);ac.setFontSize(label,17)
    button=ac.addButton(app,'RESET RUN');ac.setPosition(button,12,136);ac.setSize(button,150,28);ac.addOnClickedListener(button,reset)
    try:graphics=mmap.mmap(-1,2048,tagname='Local\\acpmf_graphics',access=mmap.ACCESS_READ)
    except Exception:pass
    return 'SRT Acceleration'

def acUpdate(dt):
    global saved
    try:
        if ac.getTrackName(0)!='srt_acceleration_75m':
            ac.setText(label,'Select SRT Acceleration 75 m');return
        if graphics is not None and struct.unpack_from('<i',graphics,4)[0]!=2:return
        p=ac.getCarState(0,acsys.CS.WorldPosition)
        row={'x':p[0],'z':p[2],'rpm':ac.getCarState(0,acsys.CS.RPM),'gear':int(ac.getCarState(0,acsys.CS.Gear))-1,'gas':ac.getCarState(0,acsys.CS.Gas),'speed_kmh':ac.getCarState(0,acsys.CS.SpeedKMH)}
        runner.update(dt,row)
        detail='GREEN start -> CHECKERED finish: 75 m'
        if runner.state=='RUN':detail='%.3f s | %.1f m | gear %s'%(runner.clock-runner.start,row['z']-runner.origin,row['gear'])
        ac.setText(label,runner.reason+'\n'+detail+'\nClutch down: 8000 two-step (CSP car)')
        if runner.result is not None and not saved:
            folder=os.path.join(os.path.expanduser('~'),'Documents','Assetto Corsa','logs')
            if not os.path.isdir(folder):os.makedirs(folder)
            path=os.path.join(folder,'srt_accel_'+time.strftime('%Y%m%d_%H%M%S')+'.json')
            with open(path,'w') as stream:json.dump({'result':runner.result,'samples':runner.rows,'car':ac.getCarName(0),'track':ac.getTrackName(0)},stream,indent=2)
            saved=True;ac.log('SRT acceleration saved '+path)
    except Exception as error:ac.setText(label,'Telemetry error: '+str(error))

def acShutdown():
    if graphics is not None:graphics.close()
