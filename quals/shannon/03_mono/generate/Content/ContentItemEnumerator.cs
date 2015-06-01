#region

using System.Collections;
using System.Collections.Generic;

#endregion

namespace Catalogizer.Core {
    public sealed class ContentItemEnumerator : IEnumerator <IContentItem> {
        private readonly IContentItem item;
        private IContentItem current;
        private bool isFirstElement;

        public ContentItemEnumerator (IContentItem item) {
            this.item = item;
            this.current = null;
        }

        #region IEnumerator<IContentItem> Members

        public void Dispose () {}

        public bool MoveNext () {
            if (this.isFirstElement) {
                this.isFirstElement = false;
                return true;
            }

            if (! this.current.HasNext ())
                return false;

            this.current = this.current.Next;
            return true;
        }

        public void Reset () {
            var first = this.item;

            while (first.HasPrev ())
                first = first.Prev;

            this.isFirstElement = true;
            this.current = first;
        }

        public IContentItem Current {
            get { return this.isFirstElement ? null : this.current; }
        }

        object IEnumerator.Current {
            get { return this.Current; }
        }

        #endregion
    }
}
