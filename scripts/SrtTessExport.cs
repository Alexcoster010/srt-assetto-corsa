using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public static class SrtTessExport {
 [STAThread] public static void Main(string[] args) { string folder=args[0];
  var app=(SldWorks)Marshal.GetActiveObject("SldWorks.Application");
  foreach(string name in new[]{"nose","front-wing","rear-wing"}) {
   string path=Path.Combine(folder,name+".SLDPRT");var doc=(ModelDoc2)app.GetOpenDocumentByName(path);
   if(doc==null)throw new Exception("Document not open: "+path);
   var part=(PartDoc)doc;var triangles=(float[])part.GetTessTriangles(true);
   using(var w=new BinaryWriter(File.Create(Path.Combine(folder,name+"-native-triangles.bin"))))foreach(float v in triangles)w.Write(v);
   Console.WriteLine(name+" triangles="+triangles.Length/9);
  }
 }
}

