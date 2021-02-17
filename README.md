SlicerQReads
============

Slicer-based implementation of 3D medical image viewer evaluated by the Mayo Clinic
to integrate with the QREADS workflow.

_This project is in active development, is not FDA approved and is not officially endorsed by the Mayo Clinic_

## Features

* Toggle between greyscale and inverted greyscale color tables
* Support max, min and mean thick slab reconstruction
* Window level presets for CT of bone, head, lung and soft-tissue
* Orientation marker in 3D and slice viewers
* Toggle reference markers visibility
* Support increasing or decreasing the brightness or contrast
* Zoom presets `100%`, `200%`, `400%`, `1:1` and `Fit to window`

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
