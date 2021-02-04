SlicerQReads
============

Slicer-based implementation of QREADS medical image viewer used at the Mayo Clinic

![SlicerQReads](Applications/SlicerQReadsApp/Resources/Images/LogoFull.png?raw=true)

## Features

* Toggle between greyscale and inverted greyscale color tables

## Table of content

* [Features](#features)
* [Command-line arguments](#command-line-arguments)
* [Maintainers](#maintainers)

## Command-line arguments

To load a DICOM series given a file in the series:

```
SlicerQReads.exe --python-code "slicer.util.loadVolume('C:/path/to/DICOM/0.dcm', {'singleFile': False})"
```

To load a DICOM series given a folder:

```
SlicerQReads.exe --python-code "folder='C:/path/to/DICOM'; import os; slicer.util.loadVolume(folder + '/' + os.listdir(folder)[0], {'singleFile': False})"
```

## Maintainers

* [Contributing](CONTRIBUTING.md)
