"""Optional AC Python 3.3 diagnostics. Read-only; never changes controls or forces."""
import ac
import acsys
import os
import time
import json
app = None
label = None
stream = None
elapsed = 0.0
samples = 0
reported = False

def acMain(ac_version):
    global app, label, stream
    app = ac.newApp('SRT Diagnostics')
    ac.setSize(app, 340, 150)
    label = ac.addLabel(app, 'Waiting for telemetry')
    ac.setPosition(label, 12, 30)
    ac.setFontSize(label, 16)
    try:
        folder = os.path.join(os.path.expanduser('~'), 'Documents', 'Assetto Corsa', 'logs')
        if not os.path.isdir(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, 'srt_driver_' + time.strftime('%Y%m%d_%H%M%S') + '.jsonl')
        stream = open(filename, 'w')
        stream.write(json.dumps({'schema': 1, 'car': ac.getCarName(0), 'track': ac.getTrackName(0), 'purpose': 'SRT FFB / brake / surface diagnosis; LastFF is game output, not measured wheel torque'}) + '\n')
    except Exception as error:
        ac.log('SRT diagnostics log unavailable: ' + str(error))
    return 'SRT Diagnostics'

def acUpdate(delta_t):
    global elapsed, samples, reported
    elapsed += delta_t
    if elapsed < 0.1:
        return
    elapsed = 0.0
    try:
        row = {'t': time.time()}
        for name in ['SpeedKMH', 'RPM', 'Gear', 'Gas', 'Brake', 'Steer', 'LastFF', 'Mz', 'Load', 'SlipRatio', 'SlipAngle', 'TyreDirtyLevel', 'TyreSurfaceDef', 'WheelAngularSpeed', 'SuspensionTravel']:
            try:
                row[name] = ac.getCarState(0, getattr(acsys.CS, name))
            except Exception:
                row[name] = None
        gear = int(row['Gear'])
        gear_text = 'R' if gear == 0 else ('N' if gear == 1 else str(gear - 1))
        ac.setText(label, 'Gear ' + gear_text + '    RPM ' + str(int(row['RPM'])) + '\nSpeed %.1f km/h\nGame FFB %+.3f\nBrake %.0f%%' % (row['SpeedKMH'], row['LastFF'], row['Brake'] * 100))
        if stream is not None and samples < 54000:
            stream.write(json.dumps(row) + '\n')
            samples += 1
            if samples % 50 == 0:
                stream.flush()
    except Exception as error:
        if not reported:
            ac.log('SRT diagnostics update: ' + str(error))
            reported = True

def acShutdown():
    if stream is not None:
        stream.close()
