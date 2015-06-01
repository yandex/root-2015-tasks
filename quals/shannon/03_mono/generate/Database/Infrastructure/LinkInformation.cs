#region

using System;
using System.Xml.Serialization;

#endregion

namespace Catalogizer.Core {
    [Serializable]
    public sealed class LinkInformation {
        [XmlAttribute ("ref")]
        public string reference;
    }
}
