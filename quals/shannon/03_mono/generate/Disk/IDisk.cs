namespace Catalogizer.Core {
    public interface IDisk {
        DiskType Type { get; }

        DiskState State { get; set; }

        DiskContentType ContentType { get; }

        DiskIndex Index { get; }

        bool Available { get; }

        string Name { get; }

        IContent Content { get; }

        FileTree FileTree { get; }
    }
}
