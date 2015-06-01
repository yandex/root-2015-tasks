#region

using System;
using System.Collections.Generic;
using System.Xml.Serialization;

#endregion

namespace Catalogizer.Core {
    [Serializable]
    [XmlRoot ("database")]
    public sealed class DatabaseInformation {
        [XmlArrayItem ("disk")]
        public List <DiskInformation> disks;
    }
}
