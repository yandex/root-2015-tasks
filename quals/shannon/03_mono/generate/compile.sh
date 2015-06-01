#!/bin/bash

mono-csc -reference:dnAnalytics.dll -out:1.exe Content/ContentItem.cs \
    Content/ContentItemEnumerator.cs \
    Content/DiskContent.cs \
    Content/IContent.cs \
    Content/IContentItem.cs \
    Database/Database.cs \
    Database/Infrastructure/ContentInformation.cs \
    Database/Infrastructure/DatabaseInformation.cs \
    Database/Infrastructure/DiskInformation.cs \
    Database/Infrastructure/FileInformation.cs \
    Database/Infrastructure/FolderInformation.cs \
    Database/Infrastructure/LinkedLinkInformation.cs \
    Database/Infrastructure/LinkInformation.cs \
    Disk/Disk.cs \
    Disk/IDisk.cs \
    Disk/Structures/DiskContentType.cs \
    Disk/Structures/DiskIndex.cs \
    Disk/Structures/DiskState.cs \
    Disk/Structures/DiskType.cs \
    FileTree/File.cs \
    FileTree/FileElementComparer.cs \
    FileTree/FileTree.cs \
    FileTree/Folder.cs \
    FileTree/IFile.cs \
    FileTree/IFileElement.cs \
    FileTree/IFolder.cs \
    FileTree/ItemType.cs \
    Program.cs
