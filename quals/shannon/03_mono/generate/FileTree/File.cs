namespace Catalogizer.Core {
    internal sealed class File : IFile {
        private string path;

        private File () {
            this.Parent = null;
            this.path = null;
        }

        public File (string name, long size)
            : this () {
            this.Name = name;
            this.Size = (ulong) size;
        }

        #region IFile Members

        public string Name { get; private set; }

        public ulong Size { get; private set; }

        public string Path {
            get {
                if (string.IsNullOrEmpty (this.path))
                    this.path = string.Format ("{0}{1}", this.Parent.Path, this.Name);

                return this.path;
            }
        }

        public IFileElement Parent { get; set; }

        #endregion
    }
}
