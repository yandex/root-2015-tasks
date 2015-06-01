#region

using System;
using System.Collections.Generic;
using System.Xml.Serialization;

#endregion

namespace Catalogizer.Core {
    [Serializable]
    public sealed class DiskInformation {
        public bool available;

        [XmlArrayItem ("item")]
        public List <ContentInformation> content;

        public DiskContentType content_type;

        public FolderInformation files;

        [XmlAttribute ("index")]
        public string index;

        public string name;
        public DiskState state;
        public DiskType type;
    }
}
