#region

using System.Collections.Generic;

#endregion

namespace Catalogizer.Core {
    public interface IContentItem : IEnumerable <IFileElement> {
        string Name { get; }
        IDisk Disk { get; }
        IContentItem Next { get; }
        IContentItem Prev { get; }

        void Add (string path);

        void Remove (string path);

        void AddNextReference (IContentItem item);
        void AddBackReference (IContentItem item);

        void RemoveNextReference ();
        void RemoveBackReference ();

        bool HasNext ();
        bool HasPrev ();
        void Rename (string name);
    }
}
