#region

using System.Collections.Generic;

#endregion

namespace Catalogizer.Core {
    public interface IContent : IEnumerable <IContentItem> {
        IDisk Disk { get; }

        IContentItem this [int index] { get; }
        IContentItem this [string name] { get; }

        void AddItem (string name);

        void RemoveItem (int index);
        void RemoveItem (IContentItem item);

        void SwapItems (int first, int second);
    }
}
