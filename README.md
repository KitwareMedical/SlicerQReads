SlicerQReads
============

Slicer-based implementation of 3D medical image viewer evaluated by the Mayo Clinic
to integrate with the QREADS workflow.

_This project is in active development, is not FDA approved and is not officially endorsed by the Mayo Clinic_

## Features

* Toggle between greyscale and inverted greyscale color tables
* Support max, min and mean thick slab reconstruction
* Window level presets for CT of bone, head, lung and soft-tissue
* Support updating the window level using the mouse
* Orientation marker in 3D and slice viewers
* Toggle reference markers visibility
* Support increasing or decreasing the brightness or contrast
* Zoom presets `100%`, `200%`, `400%`, `1:1` and `Fit to window`

## Table of content

* [Features](#features)
* [Command-line arguments](#command-line-arguments)
* [Maintainers](#maintainers)

## Command-line arguments

To load a DICOM series given a folder:

```
SlicerQReads.exe --python-code "from QReads import QReadsLogic; QReadsLogic.loadDICOMDataDirectory('C:/path/to/DICOM')"
```

## Maintainers

* [Contributing](CONTRIBUTING.md)
