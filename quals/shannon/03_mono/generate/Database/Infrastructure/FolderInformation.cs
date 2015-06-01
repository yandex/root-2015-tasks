#region

using System;
using System.Collections.Generic;
using System.Xml.Serialization;

#endregion

namespace Catalogizer.Core {
    [Serializable]
    public sealed class FolderInformation {
        [XmlArrayItem ("file")]
        public List <FileInformation> files;

        [XmlArrayItem ("folder")]
        public List <FolderInformation> folders;

        [XmlAttribute ("name")]
        public string name;
    }
}
