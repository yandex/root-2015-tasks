#region

using System.Collections.Generic;

#endregion

namespace Catalogizer.Core {
    public interface IFolder : IFileElement, IEnumerable <IFileElement> {
        IEnumerable <IFolder> Subdirectories { get; }

        IEnumerable <IFile> Files { get; }

        IFileElement this [string name] { get; }
        int Count { get; }
        int FilesCount { get; }

        void AddFile (IFile file);
        void RemoveFile (IFile file);

        void AddSubdirectory (IFolder folder);
        void RemoveSubDirectory (IFolder folder);
    }
}
