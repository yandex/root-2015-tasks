#region

using System;
using System.Xml.Serialization;

#endregion

namespace Catalogizer.Core {
    [Serializable]
    public sealed class FileInformation {
        [XmlAttribute ("name")]
        public string name;

        [XmlAttribute]
        public long size;
    }
}
