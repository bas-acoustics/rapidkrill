## Installation
This document provides installation instructions, for usage instructions see [tutorial](tutorial.md).

### Prerequisites
RAPIDKRILL requires Python 3.6. Follow installation instructions for [Linux](https://docs.python.org/3/using/unix.html), [Mac OS](https://docs.python.org/3/using/mac.html), or [Windows](https://docs.python.org/3/using/windows.html), if you have not installed yet.

### RapidKrill setup
The recommended means of installation is by cloning the git repository. If you don't already have `git` installed, follow the instructions [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

By convention, we keep code in a `src` directory:
```
# Linux & Mac OS:
mkdir ~/src
cd ~/src
git clone https://github.com/bas-acoustics/rapidkrill.git

# Windows:
mkdir C:\src
cd C:\src
git clone https://github.com/bas-acoustics/rapidkrill.git
```

### RapidKrill dependencies
The RAPIDKRILL dependencies are listed in `requirements.txt` and includes the following packages:
* [matplotlib](https://matplotlib.org/) for plotting echograms.
* [numpy](http://www.numpy.org/) for large, multi-dimensional arrays.
* [pandas](https://pypi.org/project/pandas/) for data analysis.
* [geopy](https://pypi.org/project/geopy/) python geocoding toolbox. 
* [PyEcholab](https://github.com/CI-CMG/PyEcholab) for reading echosounder files.
* [scipy](https://www.scipy.org/) for scientific computing.
* [toml](https://pypi.org/project/toml/) for configuration files.
* [sendgrid](https://github.com/sendgrid/sendgrid-python/) for sending email.
* [opencv-python](https://pypi.org/project/opencv-python/) for image processing.
* [scikit-image](https://scikit-image.org/) for image processing.
* [EchoPy](https://github.com/bas-acoustics/echopy)

The dependencies can be installed in a number of different ways depending on your system and preferences. For example, using `pip` command:
```
# Linux & Mac OS
cd ~/src/rapidkrill
pip install -r requirements.txt

# Windows
cd C:\src\rapidkrill
pip install -r requirements.txt
```

If you haven't installed `pip` yet. Follow these [instructions](https://pip.pypa.io/en/stable/installing/).
