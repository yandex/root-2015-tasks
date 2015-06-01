#region

using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Xml.Serialization;
using SystemFile = System.IO.File;

#endregion

namespace Catalogizer.Core {
    public sealed class Database : IEnumerable <IDisk> {
        private Dictionary <string, IDisk> disks;
        private string location;

        public Database (string location) {
            this.disks = new Dictionary <string, IDisk> ();
            this.location = location;
        }

        public bool Loaded {
            get { return this.location != string.Empty && this.disks.Count != 0; }
        }

        public IDisk this [string index] {
            get { return this.disks [index]; }
        }

        public IDisk this [DiskIndex index] {
            get { return this [index.ToString ()]; }
        }

        #region IEnumerable<IDisk> Members

        public IEnumerator <IDisk> GetEnumerator () {
            return this.disks.Values.GetEnumerator ();
        }

        IEnumerator IEnumerable.GetEnumerator () {
            return this.GetEnumerator ();
        }

        #endregion

        public IEnumerable <char> GetFreeLibraries () {
            const string abc = "ÀÁÂÃÄÅÆÇÈÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÛÝÞß";

            if (this.disks.Count == 0)
                return abc;

            return abc.Where (ch1 => {
                                  var collection = from pair in this.disks
                                                   let index = pair.Value.Index
                                                   where index.Letter == ch1
                                                   select index.Number;
                                  return collection.Count () == 0 ? true : collection.Max () < 99;
                              });
        }

        private static byte GetMax (IEnumerable <byte> source, byte seed) {
            return source.Count () == 0 ? seed : source.Max ();
        }

        public void AddDisk (DiskType type, DiskContentType contentType, char letter, string name, string path) {
            var number = (byte) (GetMax (from pair in this.disks
                                              let idx = pair.Value.Index
                                              where idx.Letter == letter
                                              select idx.Number,
                                              0) + 1);

            var index = new DiskIndex (letter, number);
            var disk = new Disk (index, type, name) { ContentType = contentType };
            if (path != null) {
                disk.AddFileTree (new DirectoryInfo (path));
                disk.State = DiskState.FINALIZED;
            }

            this.disks.Add (index.ToString (), disk);

            return;
        }

        public event Action OnStartDatabaseLoad;
        public event Action OnEndDatabaseLoad;
        public event Action <string> OnStartDatabaseFileLoad;
        public event Action <string> OnEndDatabaseFileLoad;
        public event Action <string> OnStartDiskLoad;
        public event Action <string> OnEndDiskLoad;
        public event Action <string> OnStartReferenceLoad;
        public event Action <string> OnEndReferenceLoad;

        public event Action OnStartDatabaseSave;
        public event Action OnEndDatabaseSave;
        public event Action <DiskIndex> OnStartDiskPreparing;
        public event Action <DiskIndex> OnEndDiskPreparing;
        public event Action <string> OnStartDatabaseFileSave;
        public event Action <string> OnEndDatabaseFileSave;

        private static void InvokeEvent <T> (Action <T> handler, T param) {
            if (handler != null)
                handler.Invoke (param);
        }

        private static void InvokeEvent (Action handler) {
            if (handler != null)
                handler.Invoke ();
        }

        public void Load () {
            if (this.Loaded)
                throw new Exception ();

            this.disks = new Dictionary <string, IDisk> ();

            var xmlSerializer = new XmlSerializer (typeof (DatabaseInformation));
            DatabaseInformation info;

            InvokeEvent (this.OnStartDatabaseLoad);

            InvokeEvent (this.OnStartDatabaseFileLoad, this.location);
            using (var fileStream = new FileStream (this.location, FileMode.Open, FileAccess.Read))
            using (var gzipStream = new GZipStream (fileStream, CompressionMode.Decompress))
                info = xmlSerializer.Deserialize (gzipStream) as DatabaseInformation;
            InvokeEvent (this.OnEndDatabaseFileLoad, this.location);

            foreach (var disk in info.disks) {
                InvokeEvent (this.OnStartDiskLoad, disk.index);
                var _disk = new Disk (disk);
                this.disks.Add (_disk.Index.ToString (), _disk);
                InvokeEvent (this.OnEndDiskLoad, disk.index);
            }

            foreach (var disk in info.disks) {
                InvokeEvent (this.OnStartReferenceLoad, disk.index);
                foreach (var content_item in disk.content) {
                    var item = this.disks [disk.index].Content [content_item.name];

                    if (content_item.backward != null && !item.HasPrev ()) {
                        var backward = content_item.backward;
                        item.AddBackReference (this.disks [backward.index].Content [backward.name]);
                    }

                    if (content_item.forward != null && !item.HasNext ()) {
                        var forward = content_item.forward;
                        item.AddNextReference (this.disks [forward.index].Content [forward.name]);
                    }
                }
                InvokeEvent (this.OnEndReferenceLoad, disk.index);
            }

            InvokeEvent (this.OnEndDatabaseLoad);
        }

        public void Save () {
            var xmlSerializer = new XmlSerializer (typeof (DatabaseInformation));
            var info = new DatabaseInformation { disks = new List <DiskInformation> () };

            InvokeEvent (this.OnStartDatabaseSave);

            foreach (var disk in from disk in this.disks
                                 select disk.Value) {
                InvokeEvent (this.OnStartDiskPreparing, disk.Index);
                info.disks.Add ((disk as Disk).ToDiskInformation ());
                InvokeEvent (this.OnEndDiskPreparing, disk.Index);
            }

            InvokeEvent (this.OnStartDatabaseFileSave, this.location);
            var tempLocation = Path.GetTempFileName ();
            using (var fileStream = new FileStream (tempLocation, FileMode.Create, FileAccess.Write))
            using (var gzipStream = new GZipStream (fileStream, CompressionMode.Compress))
                xmlSerializer.Serialize (gzipStream, info);

            if (SystemFile.Exists (this.location))
                SystemFile.Delete (this.location);
            SystemFile.Move (tempLocation, this.location);

            InvokeEvent (this.OnEndDatabaseFileSave, this.location);

            InvokeEvent (this.OnEndDatabaseSave);
        }

        public void SaveAs (string filename) {
            this.location = filename;

            this.Save ();
        }

        public void RemoveDisk (string diskIndex) {
            if (this.disks.ContainsKey (diskIndex))
                this.disks.Remove (diskIndex);
        }
    }
}
