using System;
using System.IO;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using SolidWorks.Interop.sldworks;
class SrtAssemblyExport {
 [STAThread] static void Main(string[] a) {
 var sw=(SldWorks)Marshal.GetActiveObject("SldWorks.Application");
 var doc=(ModelDoc2)sw.ActiveDoc; Console.WriteLine("ACTIVE "+doc.GetPathName());
 if(a.Length==0)return;
 Directory.CreateDirectory(a[0]);var records=new List<object>();var ass=doc as AssemblyDoc;
 if(ass==null)throw new Exception("Active document is not assembly");
 var all=(object[])ass.GetComponents(false);int id=0;
 foreach(Component2 c in all) {
 string name=c.Name2,path=c.GetPathName();bool hidden=c.IsHidden(true),suppressed=c.IsSuppressed();
 var transform=c.Transform2;double[] tr=transform==null?null:(double[])transform.ArrayData;
 var rec=new Dictionary<string,object>{{"name",name},{"source",path},{"hidden",hidden},{"suppressed",suppressed},{"transform",tr}};
 try { if(!hidden&&!suppressed) {
 var model=c.GetModelDoc2() as ModelDoc2;float[] tri=null;
 if(model is PartDoc)tri=(float[])((PartDoc)model).GetTessTriangles(true);
 else if(model==null)tri=c.GetTessTriangles(true) as float[];
 if(tri!=null&&tri.Length>0) {
 string f=(id++).ToString("D4")+".bin";using(var w=new BinaryWriter(File.Create(Path.Combine(a[0],f))))foreach(float v in tri)w.Write(v);
 rec["file"]=f;rec["triangles"]=tri.Length/9;Console.WriteLine(f+" "+name+" "+tri.Length/9);
 }
 }}catch(Exception e){rec["error"]=e.Message;}
 records.Add(rec);
 }
 var json=new JavaScriptSerializer();json.MaxJsonLength=int.MaxValue;File.WriteAllText(Path.Combine(a[0],"assembly.json"),json.Serialize(new {source=doc.GetPathName(),components=records}));
 Console.WriteLine("EXPORTED "+id+" OF "+all.Length);
 }
}
