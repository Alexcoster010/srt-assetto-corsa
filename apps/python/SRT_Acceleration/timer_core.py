"""Fixed start z=0 and finish z=75; AC Python 3.3 compatible."""
class RunTimer(object):
    def __init__(self): self.reset()
    def reset(self):
        self.state='STAGE';self.clock=0.;self.origin=0.;self.start=None
        self.previous=None;self.rows=[];self.result=None;self.gears=[];self.launch=None
        self.reason='Stage behind GREEN start line'
    def update(self,dt,row):
        if dt<=0 or dt>.25:
            if self.state=='RUN':self.state='INVALID';self.reason='Timing interrupted - reset'
            self.previous=None;return
        self.clock+=dt;row=dict(row);row['t']=self.clock
        if self.state in ('DONE','INVALID'):return
        x,z=row['x'],row['z'];prev=self.previous
        if abs(x)>2.5:
            if self.state=='RUN':self.state='INVALID';self.reason='Left corridor - reset'
            self.previous=None;return
        if prev is not None and (abs(z-prev['z'])>5 or z<prev['z']-.10):
            self.state='INVALID';self.reason='Reversed or teleported - reset';return
        if z<0 and row['speed_kmh']<.15:self.launch=dict(row)
        if self.state=='STAGE':
            if z<0:self.reason='READY - cross GREEN start line'
            if prev is not None and prev['z']<0<=z:
                fraction=-prev['z']/(z-prev['z'])
                self.start=prev['t']+fraction*(row['t']-prev['t']);self.state='RUN'
                self.rows=[dict(prev)];self.gears=[row['gear']];self.reason='RUNNING to CHECKERED finish'
            else:
                self.previous=row;return
        self.rows.append(row)
        if row['gear']>=1 and row['gear']!=self.gears[-1]:self.gears.append(row['gear'])
        if self.clock-self.start>15:self.state='INVALID';self.reason='Run exceeded 15 s';return
        if prev is not None and prev['z']<75<=z:
            fraction=(75-prev['z'])/(z-prev['z']);finish=prev['t']+fraction*(row['t']-prev['t'])
            elapsed=finish-self.start;launch=self.launch or self.rows[0]
            self.result={'time_s':elapsed,'distance_m':75,'start_z_m':0,'finish_z_m':75,'target_s':4.3,'delta_s':elapsed-4.3,'launch_rpm':launch['rpm'],'launch_gas':launch['gas'],'stationary_launch_observed':self.launch is not None,'gears':self.gears[:],'target_gear_sequence':self.gears==[2,3,4],'full_throttle_sample_fraction':sum(q['gas']>=.95 for q in self.rows)/float(len(self.rows)),'timing':'Fixed start and finish crossings using car world-position reference; interpolation at both gates','sampling_uncertainty_s':max(dt,max(self.rows[i]['t']-self.rows[i-1]['t'] for i in range(1,len(self.rows))))}
            self.state='DONE';self.reason='FINISH: %.3f s (%+.3f)'%(elapsed,elapsed-4.3)
        self.previous=row
