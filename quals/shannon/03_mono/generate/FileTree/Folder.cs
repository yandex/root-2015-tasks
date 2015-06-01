#region

using System.Collections;
using System.Collections.Generic;
using System.Linq;

#endregion

namespace Catalogizer.Core {
    internal sealed class Folder : IFolder {
        private readonly HashSet <IFileElement> elements;
        private string path;
        private ulong size;

        private Folder () {
            this.elements = new HashSet <IFileElement> ();
            this.Parent = null;
            this.path = null;
            this.size = ulong.MaxValue;
        }

        public Folder (string name)
            : this () {
            this.Name = name;
        }

        #region IFolder Members

        public string Name { get; private set; }

        public string Path {
            get {
                if (string.IsNullOrEmpty (this.path))
                    this.path = string.Format (@"{0}{1}\",
                                               this.Parent == null ? string.Empty : this.Parent.Path,
                                               this.Name);

                return this.path;
            }
        }

        public ulong Size {
            get {
                if (this.size == ulong.MaxValue)
                    this.size = this.Aggregate <IFileElement, ulong> (0, (x, elem) => x + elem.Size);

                return this.size;
            }
        }

        public int Count {
            get { return this.elements.Count; }
        }

        public int FilesCount {
            get { return this.Files.Count (); }
        }

        public IEnumerator <IFileElement> GetEnumerator () {
            return this.elements.GetEnumerator ();
        }

        IEnumerator IEnumerable.GetEnumerator () {
            return this.GetEnumerator ();
        }

        public IFileElement Parent { get; set; }

        public IEnumerable <IFolder> Subdirectories {
            get {
                return from element in this.elements
                       where element is IFolder
                       select element as IFolder;
            }
        }

        public IEnumerable <IFile> Files {
            get {
                return from element in this.elements
                       where element is IFile
                       select element as IFile;
            }
        }

        public IFileElement this [string name] {
            get { return this.elements.First (_ => _.Name == name); }
        }

        public void AddFile (IFile file) {
            this.elements.Add (file);
            (file as File).Parent = this;

            if (this.size != ulong.MaxValue)
                this.size += file.Size;
        }

        public void RemoveFile (IFile file) {
            this.elements.Remove (file);

            if (this.size != ulong.MaxValue)
                this.size -= file.Size;
        }

        public void AddSubdirectory (IFolder folder) {
            this.elements.Add (folder);
            (folder as Folder).Parent = this;

            if (this.size != ulong.MaxValue)
                this.size += folder.Size;
        }

        public void RemoveSubDirectory (IFolder folder) {
            this.elements.Remove (folder);

            if (this.size != ulong.MaxValue)
                this.size -= folder.Size;
        }

        #endregion
    }
}
