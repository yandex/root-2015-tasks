namespace Catalogizer.Core {
    public interface IFileElement {
        string Name { get; }

        string Path { get; }

        ulong Size { get; }

        IFileElement Parent { get; }
    }
}
