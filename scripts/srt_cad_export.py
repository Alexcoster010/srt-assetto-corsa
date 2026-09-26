from pathlib import Path
import urllib.request,json,uuid,shutil,hashlib,os
P=Path(os.environ['SRT_AC_PROJECT'])/'cad-r05';P.mkdir(exist_ok=True)
B=Path(os.environ['SRT26_CFD_CAD'])
def call(tool,params):
 state=json.load(urllib.request.urlopen('http://localhost:5000/api/tool/state'));body={'operationId':str(uuid.uuid4()),'stateVersion':state['stateVersion'],'tool':tool,'params':params};req=urllib.request.Request('http://localhost:5000/api/tool/execute',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'});return json.load(urllib.request.urlopen(req,timeout=100))
manifest=[]
for slug,rel in [('nose','Nose/Nose 25.SLDPRT'),('front-wing','Front Wing/SRT25 Front Wing Final CFD.SLDPRT'),('rear-wing','Rear Wing/SRT25 rear Wing Final CFD.SLDPRT')]:
 src=B/rel;dest=P/(slug+'.SLDPRT');shutil.copy2(src,dest)
 results={'open':call('open_document',{'file_path':str(dest)})}
 results['export']=call('batch_export',{'file_path_base':str(P/slug),'formats_json':'["STL","STEP"]'})
 (P/(slug+'-native-log.json')).write_text(json.dumps(results,indent=2))
 manifest.append({'source':str(src),'copy':str(dest),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_status':results['export']['status']});print(slug,results['export']['status'],flush=True)
(P/'source-manifest.json').write_text(json.dumps(manifest,indent=2))
