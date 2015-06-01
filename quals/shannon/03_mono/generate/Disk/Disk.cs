#region

using System;
using System.Collections.Generic;
using System.IO;

#endregion

namespace Catalogizer.Core {
    internal sealed class Disk : IDisk {
        private Disk () {
            this.Type = DiskType.CD_ROM;
            this.State = DiskState.CLEAR;
            this.ContentType = DiskContentType.DOCUMENTS;
            this.Index = new DiskIndex ('À', 01);
            this.Available = true;
            this.Name = string.Empty;
            this.Content = new DiskContent (this);
            this.FileTree = null;
        }

        public Disk (DiskIndex index, DiskType type, string name)
            : this () {
            this.Index = index;
            this.Type = type;
            this.Name = name;
        }

        internal Disk (DiskInformation info) {
            this.Type = info.type;
            this.State = info.state;
            this.ContentType = info.content_type;
            this.Index = DiskIndex.Parse (info.index);
            this.Available = info.available;
            this.Name = info.name;

            if (info.files != null)
                this.FileTree = new FileTree (this, info);

            if (info.content != null)
                this.Content = new DiskContent (this, info);
        }

        #region IDisk Members

        public DiskType Type { get; private set; }

        public DiskState State { get; set; }

        public DiskContentType ContentType { get; set; }

        public DiskIndex Index { get; private set; }

        public bool Available { get; set; }

        public string Name { get; private set; }

        public IContent Content { get; private set; }

        public FileTree FileTree { get; private set; }

        #endregion

        internal void AddFileTree (DirectoryInfo info) {
            if (this.FileTree != null)
                throw new ArgumentException ();

            this.FileTree = FileTree.CreateFileTree (this, info);
        }

        internal DiskInformation ToDiskInformation () {
            var result = new DiskInformation {
                                                 index = this.Index.ToString (),
                                                 type = this.Type,
                                                 state = this.State,
                                                 content_type = this.ContentType,
                                                 available = this.Available,
                                                 name = this.Name,
                                                 content = new List <ContentInformation> ()
                                             };

            foreach (var content_item in this.Content) {
                var content = new ContentInformation {
                                                         name = content_item.Name,
                                                         backward = content_item.HasPrev ()
                                                                        ? new LinkedLinkInformation {
                                                                                                        index =
                                                                                                            content_item
                                                                                                            .Prev.Disk.
                                                                                                            Index.
                                                                                                            ToString (),
                                                                                                        name =
                                                                                                            content_item
                                                                                                            .Prev.Name
                                                                                                    }
                                                                        : null,
                                                         forward = content_item.HasNext ()
                                                                       ? new LinkedLinkInformation {
                                                                                                       index =
                                                                                                           content_item.
                                                                                                           Next.Disk.
                                                                                                           Index.
                                                                                                           ToString (),
                                                                                                       name =
                                                                                                           content_item.
                                                                                                           Next.Name
                                                                                                   }
                                                                       : null,
                                                         file_links = new List <LinkInformation> ()
                                                     };

                foreach (var file_link in content_item)
                    content.file_links.Add (new LinkInformation { reference = file_link.Path });

                result.content.Add (content);
            }

            if (this.FileTree != null) {
                result.files = new FolderInformation ();
                this.SaveFolderInformation (result.files, this.FileTree.Root as IFolder);
            }

            return result;
        }

        internal void SaveFolderInformation (FolderInformation to, IFolder folder) {
            to.name = folder.Name;
            to.files = new List <FileInformation> ();
            to.folders = new List <FolderInformation> ();

            foreach (var file in folder.Files)
                to.files.Add (new FileInformation { name = file.Name, size = (long) file.Size });

            foreach (var subdirectory in folder.Subdirectories) {
                var subfolder = new FolderInformation ();
                this.SaveFolderInformation (subfolder, subdirectory);

                to.folders.Add (subfolder);
            }
        }
    }
}
