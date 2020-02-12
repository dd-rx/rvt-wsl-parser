#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   ~~~~~~~~~##\~~~~~~~##\~~~~~~~~~~~~~~~~~~~~~~~
#   ~~~~~~~~~## |~~~~~~## |~~~~~~~~~~~~~~~~~~~~~~
#   ~~~~####### |~####### |~######\~##\~~~##\~~~~
#   ~~~##  __## |##  __## |##  __##\\##\~##  |~~~
#   ~~~## /~~## |## /~~## |## |~~\__|\####  /~~~~
#   ~~~## |~~## |## |~~## |## |~~~~~~##  ##<~~~~~
#   ~~~\####### |\####### |## |~~~~~##  /\##\~~~~
#   ~~~~\_______|~\_______|\__|~~~~~\__/~~\__|~~~
#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   ~~~~~~~~~~~~ deductive reasoning ~~~~~~~~~~~~

#   copyright 2020 by m.wild for ddrx
#   contact mail@ddrx.ch
#   public  repo https://bitbucket.org/ddrx/revit-worksharingjournal-reader/

#   last updated: 12/02/2020


##  DESCRIPTION

#   !THIS IS WORK IN PROGRESS!
#   this is a parser vor revit worksharingjournals (*.slog) to make it human-readable.
#   later it should allow to disect the data by user or event and get timing on events.
#
#   Autodesk Knowledge Network:
#   https://knowledge.autodesk.com/support/revit-products/troubleshooting/caas/simplecontent/content/how-to-read-the-revit-worksharing-log-slog-file.html
#
#   variables starting with _ are meant for temporary use in loops and functions
#   for readability using dictionaries instead of lists

##  LICENSE AGREEMENT

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.


# ------------------------------------------- #

##  IMPORTS

import re
import codecs
from datetime import datetime


## FUNCTIONS


def RegexToDict(_input):
    _dict = [dict(_session.groupdict()) for _session in _input]
    return _dict


def FormatDateTime(_date, _time):
    _date = datetime.strptime(_date, "%Y-%m-%d").date()
    _time = datetime.strptime(_time, "%H:%M:%S").time()
    return _date, _time


def CalculateDuration(_start, _end):
    # calculate syncduration
    _tmpstart = datetime.combine(_start["date"], _start["time"])
    _tmpend = datetime.combine(_end["date"], _end["time"])
    _duration = _tmpend - _tmpstart
    return _duration


def SessionOverview(_sessiondata, _v=3):
    if _v == 3:
        for _session in _sessiondata:
            print(
                f'{_session["date"]}, {_session["time"]} | {_session["sid"]} {_session["user"]} - {_session["build"]} {_session["host"]}'
            )
    elif _v == 2:
        for _session in _sessiondata:  # [-10:] last 10 entries
            print(
                str(_session["date"])
                + ", "
                + str(_session["time"])
                + " | "
                + _session["sid"]
                + " "
                + _session["user"]
                + " - "
                + _session["build"]
                + " "
                + _session["host"]
            )


# ------------------------------------------- #

##  SET UP TIMER

starttime = datetime.now()


# ------------------------------------------- #

##  REGEX
# !!! gingercareful: depending on python implementation named groups are defined by ?<foo> ?P<foo> or maybe others. assigned as raw bytes.


# trying to make the regex modular...
# regex_base is reused for all patterns. gets sessionid date time
regex_base = r"""(?P<sid>\$[0-9a-fA-F]{8}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]{3})."""

# different selectors
regex_select_all = r"""(?P<action>\>|\<|\.)(?P<event>[^\s]*)(?P<parameter>.*)\r"""
regex_select_alltransactions = (
    r"""(?P<action>\>|\<)(?P<event>[^\s]*)(?P<parameter>.*)\r"""
)
regex_select_allevents = r"""(?P<action>\.)(?P<event>[^\s]*)(?P<parameter>.*)\r"""
regex_select_stcstl = r"""(?P<action>\>|\<)(?P<event>STC:STL)\r"""
regex_select_stc = r"""(?P<action>\>|\<)(?P<event>STC)\r"""
regex_select_stcstcstl = r"""(?P<action>\>|\<)(?P<event>STC|STC:STL)\r"""
regex_select_allstc = r"""(?P<action>\>|\<)(?P<event>STC.*)\r"""

# regex_housekeeping = re.compile(r"""(?P<name>\b_[a-zA-Z0-9]+[a-zA-Z0-9_]*[a-zA-Z0-9])""")

# put the regex together. change the second part
regex = re.compile(regex_base + regex_select_all)

# grab session informations to assign user to sessionID, also get build version and the host....
regex_sid = re.compile(
    r"""(?P<sid>\$.[0-9a-fA-F]{7}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}).*\n\s\buser\=.(?P<user>\b.*\b).*\n\s\bbuild\=.(?P<build>\b.*\b.).*\n\s\bjournal\=.(?P<journal>\b.*\b).*\n\s\bhost\=(?P<host>.*.)\r"""
)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
#   "We interrupt this program to annoy you       #
#   and make things generally more irritating."   #
#            -Monty Python's Flying Circus        #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


# ------------------------------------------- #

##  READING DATA

# read WorkSharingJournal
# !!! opening UCS-2-LE .slog as UTF-16-LE ... *duck&run*
wsj = codecs.open(r"""./sampledata/sample.slog""", "r", encoding="utf-16")
wsjdata = wsj.read()
wsj.close()
# housekeeping
del wsj

# getting user sessiondata
sessiondata = regex_sid.finditer(wsjdata, re.MULTILINE)
# getting events (set regex above)
journaldata = regex.finditer(wsjdata)

# housekeeping
del regex
del regex_sid
del wsjdata


##  PROCESSING DATA

# regex to dictionary
sessiondata = RegexToDict(sessiondata)
journaldata = RegexToDict(journaldata)


# finessing the sessiondata
for _session in sessiondata:
    # add user to journalevents
    for _entry in journaldata:
        if _entry["sid"] == _session["sid"]:
            _entry["user"] = _session["user"]
    # date/time formatting
    _session["date"], _session["time"] = FormatDateTime(
        _session["date"], _session["time"]
    )

del _session
del _entry

# print(len(globals()))
# print(dir())

# def maid(input):
#     housekeeping = regex_housekeeping.finditer(str(input))
#     housekeeping= [dict(_var.groupdict()) for _var in housekeeping]
#     print(len(dir()))
#     print(housekeeping)
#     for _var in housekeeping:
#         print(_var['name'])
#         if _var['name']!='_frozen_importlib_external':
#             del globals()[_var['name']]
#     print(len(dir()))
#     print(housekeeping)
#     #del _var, housekeeping

# unfinished housmaid
# housekeeping = regex_housekeeping.finditer(str(globals()))
# housekeeping= [dict(_var.groupdict()) for _var in housekeeping]
# print(len(dir()))
# print(dir())
# for _var in housekeeping:
#     print(_var['name'])
#     if _var['name']!='_frozen_importlib_external':
#         del globals()[_var['name']]
# del _var, housekeeping
# print(len(dir()))
# print(dir())
# #del _var, housekeeping
#
# breakpoint()


synctocentral = []

# finessing the journaldata
for _index, _entry in enumerate(journaldata):
    # date/time formatting
    _entry["date"], _entry["time"] = FormatDateTime(_entry["date"], _entry["time"])

    # assign index
    _entry["index"] = _index

    # clean up two leading spaces in parameter
    if _entry["parameter"]:
        _entry["parameter"] = _entry["parameter"][2:]

    # get beginning of sync event
    if _entry["action"] == ">" and _entry["event"] == "STC":
        synctocentral.append({"syncstart": _index, "syncend": ""})

    # get end of sync event | #TODO how to detect unfinished syncs??
    if _entry["action"] == "<" and _entry["event"] == "STC":
        # TODO how stupid is it to assume there is only one open syncronisation per user so i can stop matching after first hmatch when going thru the list backwards..?!
        for _sync in synctocentral[::-1]:
            if (
                not _sync["syncend"]
                and journaldata[_sync["syncstart"]]["sid"] == _entry["sid"]
            ):
                _sync["syncend"] = _index

                # calculate syncduration
                _sync["syncduration"] = CalculateDuration(
                    journaldata[_sync["syncstart"]], journaldata[_sync["syncend"]]
                )

                break


# ------------------------------------------- #

##  DELIVERING RESULTS

SessionOverview(sessiondata)

print("---")

for _entry in journaldata[-20:]:  # [-10:] last 10 entries
    print(
        str(_entry["date"])
        + " "
        + str(_entry["time"])
        + " | "
        + _entry["action"]
        + "  "
        + _entry["event"]
        + " | "
        + _entry["sid"]
        + " "
        + _entry["user"]
        + " | "
        + str(_entry["index"])
    )

print("---")

for _entry in synctocentral[-20:]:
    print(
        str(journaldata[_entry["syncstart"]]["date"])
        + " "
        + str(journaldata[_entry["syncstart"]]["time"])
        + " - "
        + str(journaldata[_entry["syncend"]]["time"])
        + " :: "
        + str(int(_entry["syncduration"].total_seconds()))
        + "s | "
        + journaldata[_entry["syncstart"]]["event"]
        + " | "
        + journaldata[_entry["syncstart"]]["sid"]
        + " "
        + journaldata[_entry["syncstart"]]["user"]
        + " @ "
        + str(journaldata[_entry["syncstart"]]["index"])
        + " :: "
        + journaldata[_entry["syncend"]]["sid"]
        + " "
        + journaldata[_entry["syncend"]]["user"]
        + " @ "
        + str(journaldata[_entry["syncend"]]["index"])
    )


# ------------------------------------------- #
# housekeeping
del journaldata
del sessiondata

##  PRINT RUNTIME

endtime = datetime.now()
print("\nruntime:")
print(endtime - starttime)
