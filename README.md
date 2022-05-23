# PDFview
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/tmattick/PDFview?sort=semver) ![GitHub last commit](https://img.shields.io/github/last-commit/tmattick/PDFview) ![GitHub top language](https://img.shields.io/github/languages/top/tmattick/PDFview)

PDFview is a GUI application for visualizing and working with pair distribution functions (PDFs). Functionalities include plotting, scaling, calculating differential PDFs (dPDFs) and fast determination of local extrema. PDFview is made to work with files created either with [PDFgetX3](https://www.diffpy.org/products/pdfgetx.html) or [PDFgui](https://www.diffpy.org/products/pdfgui.html). However, there is a fallback mode for unknown files that should be able to analyze any plain text file containing columns of x, y pairs seperated by one or more spaces. 
The entire application is part of a master's thesis.

## Installation

There are binaries available for Windows, Linux and Mac OS via the [release page](https://github.com/tmattick/PDFview/releases). All these versions have already been tested, with the Windows version being the most thoroughly tested.
Alternatively, you can run the Python scripts yourself, which will probably improve performance, though not much. If there is a Python interpreter on your system, simply clone the repository, install the listed dependencies either manually or (recommended) via the [requirements.txt](./requirements.txt) and run the [main.py](./main.py).
```
git clone https://github.com/tmattick/PDFview.git
cd PDFview
pip install -r requirements.txt
python main.py
```

## Dependencies

- Python >= 3.8
- numpy
- scipy
- matplotlib
- PySimpleGUI

PDFview also uses TKinter for the graphical user interface, which is usually included in every standard Python installation. However, there are some Python installations which do not include TKinter, especially for Mac OS. Since this may cause problems when running the PDFview GUI, please check whether your Python installation includes TKinter before installing PDFview via the Python route.

## License

> You can check out the full license [here](https://github.com/tmattick/PDFview/blob/main/LICENSE).

This project is licensed under the terms of the **MIT license**.
