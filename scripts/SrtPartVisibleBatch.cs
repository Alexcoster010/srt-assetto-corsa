using System;using System.IO;using System.Collections.Generic;using System.Runtime.InteropServices;using System.Web.Script.Serialization;using SolidWorks.Interop.sldworks;
class SrtPartBatch { [STAThread] static void Main(string[] a) {
 var sw=(SldWorks)Marshal.GetActiveObject("SldWorks.Application");var js=new JavaScriptSerializer();js.MaxJsonLength=int.MaxValue;
 var paths=js.Deserialize<string[]>(File.ReadAllText(a[0]));Directory.CreateDirectory(a[1]);var rows=new List<object>();int i=0;
 foreach(var path in paths) {var r=new Dictionary<string,object>{{"source",path}};string f=(i++).ToString("D4")+".bin";
 try{var doc=(ModelDoc2)sw.GetOpenDocumentByName(path);bool opened=doc==null;int e=0,warn=0;if(opened)doc=sw.OpenDoc6(path,1,3,"",ref e,ref warn);r["open_error"]=e;r["open_warning"]=warn;
 if(doc!=null) {var points=new List<float>();var bodies=((PartDoc)doc).GetBodies2(-1,true) as object[];r["visible_bodies"]=bodies==null?0:bodies.Length;if(bodies!=null)foreach(Body2 body in bodies){var faces=body.GetFaces() as object[];if(faces!=null)foreach(Face2 face in faces){var ft=face.GetTessTriangles(true) as float[];if(ft!=null)points.AddRange(ft);}}var tri=points.ToArray();if(tri!=null){using(var w=new BinaryWriter(File.Create(Path.Combine(a[1],f))))foreach(float v in tri)w.Write(v);r["file"]=f;r["triangles"]=tri.Length/9;Console.WriteLine(f+" "+tri.Length/9+" "+Path.GetFileName(path));}if(opened)sw.CloseDoc(doc.GetTitle());}
 }catch(Exception e){r["error"]=e.Message;Console.WriteLine("ERROR "+Path.GetFileName(path)+" "+e.Message);}rows.Add(r);File.WriteAllText(Path.Combine(a[1],"parts.json"),js.Serialize(rows));
 }
 }}

