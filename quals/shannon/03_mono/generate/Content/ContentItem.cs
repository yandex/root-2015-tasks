#region

using System.Collections;
using System.Collections.Generic;

#endregion

namespace Catalogizer.Core {
    internal sealed class ContentItem : IContentItem {
        private readonly HashSet <IFileElement> content;

        private ContentItem () {
            this.content = new HashSet <IFileElement> (FileElementComparer.Instance);
            this.Next = null;
            this.Prev = null;
        }

        public ContentItem (string name, IDisk disk)
            : this () {
            this.Name = name;
            this.Disk = disk;
        }

        #region IContentItem Members

        public string Name { get; private set; }

        public IDisk Disk { get; private set; }

        public void Add (string path) {
            this.content.Add (this.Disk.FileTree.GetElement (path));
        }

        public void Remove (string path) {
            this.content.Remove (this.Disk.FileTree.GetElement (path));
        }

        public void AddNextReference (IContentItem item) {
            if (this.Next != null) {
                var iter = item;
                while (iter.HasNext ())
                    iter = iter.Next;
                var next = this.Next;

                this.Next = item;
                (item as ContentItem).Prev = this;

                (iter as ContentItem).Next = next;
                (next as ContentItem).Prev = iter;
            }

            this.Next = item;
            (item as ContentItem).Prev = this;
        }

        public void AddBackReference (IContentItem item) {
            if (this.Prev != null) {
                var iter = item;
                while (iter.HasPrev ())
                    iter = iter.Prev;
                var prev = this.Prev;

                this.Prev = item;
                (item as ContentItem).Next = this;

                (iter as ContentItem).Prev = prev;
                (prev as ContentItem).Next = iter;
            }

            this.Prev = item;
            (item as ContentItem).Next = this;
        }

        public void RemoveNextReference () {
            if (this.Next == null)
                return;

            (this.Next as ContentItem).Prev = null;
            this.Next = null;
        }

        public void RemoveBackReference () {
            if (this.Prev == null)
                return;

            (this.Prev as ContentItem).Next = null;
            this.Prev = null;
        }

        public IContentItem Next { get; private set; }

        public IContentItem Prev { get; private set; }

        public bool HasNext () {
            return this.Next != null;
        }

        public bool HasPrev () {
            return this.Prev != null;
        }

        public void Rename (string name) {
            this.Name = name;
        }

        public IEnumerator <IFileElement> GetEnumerator () {
            return this.content.GetEnumerator ();
        }

        IEnumerator IEnumerable.GetEnumerator () {
            return this.GetEnumerator ();
        }

        #endregion

        public override string ToString () {
            return string.Format ("{0}::{1}", this.Disk.Index, this.Name);
        }
    }
}
