#region

using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;

#endregion

namespace Catalogizer.Core {
    public sealed class FileTree {
        private FileTree () {}

        internal FileTree (IDisk disk, DiskInformation info) {
            this.Disk = disk;
            this.Root = new Folder (disk.Index.ToString ());

            this.ProcessDirectory (info.files, this.Root as IFolder);
        }

        public IFileElement Root { get; private set; }
        public IDisk Disk { get; private set; }

        public IFileElement GetElement (string path) {
            using (var pathEnumerator = new PathEnumerator (path)) {
                pathEnumerator.Reset ();

                if (! pathEnumerator.MoveNext ())
                    throw new ArgumentException ();

                if (pathEnumerator.Current != this.Disk.Index.ToString ())
                    throw new ArgumentException ();

                var element = this.Root;
                while (pathEnumerator.MoveNext ()) {
                    if (! (element is IFolder))
                        throw new ArgumentException ();

                    element = (element as IFolder) [pathEnumerator.Current];
                }

                return element;
            }
        }

        public static FileTree CreateFileTree (IDisk disk, DirectoryInfo directory) {
            var result = new FileTree { Disk = disk, Root = new Folder (disk.Index.ToString ()) };

            ProcessDirectory (directory, result.Root as IFolder);

            return result;
        }

        public static string ExtractDiskIndex (string path) {
            using (var pathEnumerator = new PathEnumerator (path)) {
                pathEnumerator.Reset ();

                if (! pathEnumerator.MoveNext ())
                    throw new ArgumentException ();

                return pathEnumerator.Current;
            }
        }

        private void ProcessDirectory (FolderInformation files, IFolder folder) {
            foreach (var file in files.files)
                folder.AddFile (new File (file.name, file.size));

            foreach (var subdirectory in files.folders) {
                var subfolder = new Folder (subdirectory.name);
                this.ProcessDirectory (subdirectory, subfolder);

                folder.AddSubdirectory (subfolder);
            }
        }

        private static void ProcessDirectory (DirectoryInfo directory, IFolder folder) {
            foreach (var file in directory.GetFiles ())
                folder.AddFile (new File (file.Name, file.Length));

            foreach (var subdirectory in directory.GetDirectories ()) {
                var subfolder = new Folder (subdirectory.Name);
                ProcessDirectory (subdirectory, subfolder);

                folder.AddSubdirectory (subfolder);
            }
        }

        public static ItemType GetItemType (string item) {
            return item.Length < 1 || item [item.Length - 1] == '\\' ? ItemType.FOLDER_ITEM : ItemType.FILE_ITEM;
        }

        #region Nested type: PathEnumerator

        private sealed class PathEnumerator : IEnumerator <string> {
            private readonly string str;
            private int first;
            private int last;

            public PathEnumerator (string str) {
                this.str = str;
            }

            #region IEnumerator<string> Members

            public void Dispose () {}

            public bool MoveNext () {
                this.first = this.last;

                if (this.first >= this.str.Length - 1)
                    return false;

                do {
                    ++this.last;
                } while (this.last < this.str.Length && this.str [this.last] != '\\');

                return true;
            }

            public void Reset () {
                this.first = -1;
                this.last = -1;
            }

            public string Current {
                get { return this.str.Substring (this.first + 1, this.last - (this.first + 1)); }
            }

            object IEnumerator.Current {
                get { return this.Current; }
            }

            #endregion
        }

        #endregion
    }
}
