#region

using System.Collections.Generic;

#endregion

namespace Catalogizer.Core {
    public sealed class FileElementComparer : IEqualityComparer <IFileElement> {
        public static readonly FileElementComparer Instance = new FileElementComparer ();

        #region IEqualityComparer<IFileElement> Members

        public bool Equals (IFileElement x, IFileElement y) {
            return (x.Name == y.Name) && (x.Path == y.Path);
        }

        public int GetHashCode (IFileElement obj) {
            return obj.GetHashCode ();
        }

        #endregion
    }
}
