# boreholetools
*VERSION: 0.0.2*
*LAST CHANGE: 2019/04/12*

boreholetools is a collection of modules to QC geoscientific borehole data of various types

Main features:

* convert/verify/interpolate well trajectory data, i.e. deviation surveys
* convert apparent bed dip/dip azimuth data referenced to a wellbore coordinate system into true bed dip/dip azimuth
* calculate true vertical/stratigraphic thickness of beds using a dip model

Default behavior of modules unless specified otherwise by using additional keyword arguments:

* reads a list of well data in the form of CSV spread sheet files
* processes one or many well data in one iteration
* output generated will be another set of CSV files replacing the previous run

```note: Documentation in progress...```

## Getting Started

### Prerequisites

Only Python 3 standard library modules are used currently.

### Installation

1. Install Python version 3.6.3 or later
2. Clone the respective project repository from github:  
```git clone https://github.com/mavost/boreholetools.git```

3. Invoke a test run of all modules using no arguments and default input files residing in `/data`:  
```python boreholetools.py --testing```

4. If testing run was successful a default run requires a number of keyword arguments for accessing the desired behavior and input files to support the processing:  
```python boreholetools.py KEYWORDS```

### Function and Keyword Description
A brief self-documentation of keywords and operational modes is invoked on command line using:
```python boreholetools.py --help```
Example input files reside in `/data`.

```note: Documentation in progress...```

## Built With

The project was developed using Python version 3.6.3 on a Windows 7 x64 machine.

## Versioning

We use [Git](http://git-scm.com/) for versioning and [Sphinx](http://www.sphinx-doc.org/) for documentation.

## Authors

* **Markus von Steht** - *Initial work* - [mavost](https://github.com/mavost)

See also the list of [contributors](https://github.com/mavost/boreholetools/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* **Billie Thompson** - *README template* - [on github.com](https://github.com/PurpleBooth)
* **Rich Yap** - *A Simple Tutorial on How to document your Python Project using Sphinx* - [on medium.com](https://medium.com/@richyap13/a-simple-tutorial-on-how-to-document-your-python-project-using-sphinx-and-rinohtype-177c22a15b5b)
* **Miller Medeiros** - *A default CSS file* - [on github.com](https://gist.github.com/millermedeiros/771852)
* Sawaryn, S. J., & Thorogood, J. L. (2005, March 1). A Compendium of Directional Calculations Based on the Minimum Curvature Method. Society of Petroleum Engineers. doi:10.2118/84246-PA [Link](https://www.onepetro.org/journal-paper/SPE-84246-PA)
* etc
