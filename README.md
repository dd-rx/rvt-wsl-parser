[![DDRX](https://img.shields.io/badge/DD-RX-333?style=for-the-badge)](https://ddrx.ch)
***
![STATUS TESTING](https://img.shields.io/badge/STATUS-TESTING-orange?style=flat-square&logo=koding&logoColor=white)




## revit-worksharing-log parser

![what for](https://img.shields.io/badge/use_with-Revit-yellow?style=flat-square&logo=ipfs&logoColor=white)
![who for](https://img.shields.io/badge/user-BIM--Manager-yellow?style=flat-square&logo=tapas&logoColor=white)
![requires python > 3.6](https://img.shields.io/badge/requires-python%20%3E3.6-lightgrey?style=flat-square&logo=graphql&logoColor=white)
[![requires python < 3.6 with future-fstings](https://img.shields.io/badge/requires-python%20%3C%203.6%20%2B%20future--fstrings-lightgrey?style=flat-square&logo=graphql&logoColor=white)](https://img.shields.io/badge/requires-python%20%3C%203.6%20%2B%20future--fstrings-lightgrey)
---


simple tool to make the revit worksharingjournal human-readable
by either simply exporting the revit worksharing log as a .csv file that can be analyzed in excel or some quick summaries in the console.

#### usage

`>>>wslparser.py export sync 'x:\some\path\your-worksharingjournal.slog'`
`>>>wslparser.py` _`mode` `dataset` `'path'`_

- mode
  * `export` exports the selected dataset as `[date]_[model].csv` file in the same location as the revit .slog file.
  * `show` this option gives you a quick look at some summaries.
- dataset select which events to export.
  * `sessions` `sessions-detailed` `syncs` `syncs-detailed`
- path
  * path to the revit .slog file. either full path or relative. must be in quotes.

_because i used fstrings for easier formatting of console output you need python >3.6 or [future-fstrings](https://img.shields.io/badge/requires-python%20%3C%203.6%20%2B%20future--fstrings-lightgrey) for console usage.
csv export is unaffected by this._

_in case you need a portable version of python that works without installing or administrative privileges, [winpython](https://winpython.github.io/) is for you._

___
[![PyCharm](https://img.shields.io/badge/IDE-PyCharm-yellowgreen?style=flat-square&logo=jetbrains&logoColor=white)](https://www.jetbrains.com/pycharm/)
[![Made with Python](https://img.shields.io/badge/made%20with-python-yellowgreen.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square&logo=styled-components&logoColor=white)](https://github.com/psf/black)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-black.svg?style=flat-square&logo=styled-components&logoColor=white)](https://www.python.org/dev/peps/pep-0008/)
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square&logo=gnu&logoColor=white)](https://www.gnu.org/licenses/gpl-3.0.en.html)
---
[![gitlab](https://img.shields.io/badge/main-gitlab-lightgrey?style=flat-square&logo=GitLab&logoColor=white)](https://git.ddrx.ch/ddrx/revit-worksharingjournal-reader)
[![bitbucket](https://img.shields.io/badge/mirror-bitbucket-lightgrey?style=flat-square&logo=Bitbucket&logoColor=white)](https://bitbucket.org/%7B447fac70-6865-48c1-9f3c-d3f45dea8388%7D/)
