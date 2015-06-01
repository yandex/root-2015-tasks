#region

using System.Collections;
using System.Collections.Generic;
using System.Linq;

#endregion

namespace Catalogizer.Core {
    public sealed class DiskContent : IContent {
        private readonly IList <IContentItem> items;

        public DiskContent (IDisk disk) {
            this.Disk = disk;
            this.items = new List <IContentItem> ();
        }

        internal DiskContent (IDisk disk, DiskInformation info)
            : this (disk) {
            foreach (var item in info.content) {
                var _item = new ContentItem (item.name, disk);

                foreach (var link in item.file_links)
                    _item.Add (link.reference);

                this.items.Add (_item);
            }
        }

        #region IContent Members

        public IEnumerator <IContentItem> GetEnumerator () {
            return this.items.GetEnumerator ();
        }

        IEnumerator IEnumerable.GetEnumerator () {
            return this.GetEnumerator ();
        }

        public IDisk Disk { get; private set; }

        public IContentItem this [int index] {
            get { return this.items [index]; }
        }

        IContentItem IContent.this [string name] {
            get { return this.items.First (_ => _.Name == name); }
        }

        public void AddItem (string name) {
            this.items.Add (new ContentItem (name, this.Disk));
        }

        public void RemoveItem (int index) {
            this.RemoveItem (this [index]);
        }

        public void RemoveItem (IContentItem item) {
            if (!this.items.Remove (item))
                return;

            var next = item.Next;
            var prev = item.Prev;

            item.RemoveNextReference ();
            item.RemoveBackReference ();

            if (next == null || prev == null)
                return;

            prev.AddNextReference (next);
        }

        public void SwapItems (int first, int second) {
            var item = this [first];
            this.items [first] = this [second];
            this.items [second] = item;
        }

        #endregion
    }
}
