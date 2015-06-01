#region

using System;
using System.Collections.Generic;
using System.Xml.Serialization;

#endregion

namespace Catalogizer.Core {
    [Serializable]
    public sealed class ContentInformation {
        public LinkedLinkInformation backward;

        [XmlArrayItem ("link")]
        public List <LinkInformation> file_links;

        public LinkedLinkInformation forward;

        [XmlAttribute ("name")]
        public string name;
    }
}
