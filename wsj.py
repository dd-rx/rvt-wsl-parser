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
#   repo https://bitbucket.org/ddrx/revit-worksharingjournal-reader/

#   last updated: 12/02/2020


##  DESCRIPTION

#   !THIS IS WORK IN PROGRESS!
#   this is a parser vor revit worksharingjournals (*.slog) to make it human-readable.
#   later it should allow to disect the data by user or event and get timing on events.
#
#   Autodesk Knowledge Network: https://knowledge.autodesk.com/support/revit-products/troubleshooting/caas/simplecontent/content/how-to-read-the-revit-worksharing-log-slog-file.html
#

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
wsj = codecs.open(r"""./sampledata/realsample.slog""", "r", encoding="utf-16")
wsjdata = wsj.read()
wsj.close()
# clear readbuffer
wsl = 0

# getting user sessiondata
sessiondata = regex_sid.finditer(wsjdata, re.MULTILINE)
# getting events (set regex above)
journaldata = regex.finditer(wsjdata)
# clear raw data
wsjdata = 0


##  PROCESSING DATA

# regex to dictionary
sessiondata = [dict(_session.groupdict()) for _session in sessiondata]
journaldata = [dict(_entry.groupdict()) for _entry in journaldata]


# finessing the sessiondata
for _session in sessiondata:
    # add user to journalevents
    for _entry in journaldata:
        if _entry["sid"] == _session["sid"]:
            _entry["user"] = _session["user"]
    # date/time formatting
    _session["date"] = datetime.strptime(_session["date"], "%Y-%m-%d").date()
    _session["time"] = datetime.strptime(_session["time"], "%H:%M:%S").time()


# finessing the journaldata
synctocentral = []

for _index, _entry in enumerate(journaldata):
    # date/time formatting
    _entry["date"] = datetime.strptime(_entry["date"], "%Y-%m-%d").date()
    _entry["time"] = datetime.strptime(_entry["time"], "%H:%M:%S").time()
    # assign index
    _entry["index"] = _index
    # get beginning of sync event
    if _entry["action"] == ">" and _entry["event"] == "STC":
        synctocentral.append({"syncstart": _index, "syncend": ""})
    # get end of sync event | #TODO how to detect unfinished syncs??
    if _entry["action"] == "<" and _entry["event"] == "STC":
        # TODO how stupid is it to assume there is only one open syncronisation per user so i can stop matching after first hmatch when going thru the list backwards..?!
        _hit = 0
        for _sync in synctocentral[::-1]:
            if (
                not _sync["syncend"]
                and journaldata[_sync["syncstart"]]["sid"] == _entry["sid"]
                # and journaldata[sync["syncstart"]]["user"] == entry["user"] # unnecessary
                and not _hit
            ):
                _sync["syncend"] = _index
                # calculate syncduration
                _tmpsyncstart = datetime.combine(
                    journaldata[_sync["syncstart"]]["date"],
                    journaldata[_sync["syncstart"]]["time"],
                )
                _tmpsyncend = datetime.combine(
                    journaldata[_sync["syncend"]]["date"],
                    journaldata[_sync["syncend"]]["time"],
                )
                _sync["syncduration"] = _tmpsyncend - _tmpsyncstart
                _hit = 1

    # clean up two leading spaces in parameter
    if _entry["parameter"]:
        _entry["parameter"] = _entry["parameter"][2:]


# ------------------------------------------- #

##  DELIVERING RESULTS

for _session in sessiondata[-10:]:  # [-10:] last 10 entries
    print(
        str(_session["date"])
        + " "
        + str(_session["time"])
        + " | "
        + _session["build"]
        + " | "
        + _session["sid"]
        + " "
        + _session["user"]
    )

print("---")

for _entry in journaldata[-20:]:  # [-10:] last 10 entries
    # print(entry)
    # if entry['user']=='marco.wild':
    #    print(str(entry['date'])+' '+str(entry['time'])+' | '+entry['action']+'  '+entry['event']+' | '+entry['sid']+' '+entry['user']+' | '+str(entry['index']))
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
# print([list(i) for i in journaldata])
# print(synctocentral)
for _entry in synctocentral[-20:]:
    # print(entry)
    # print(entry['syncduration'].total_seconds())
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
    # print(journaldata[entry['syncstart']])
    # print(journaldata[entry['syncend']])
    # print(str(journaldata[entry['syncstart']]['date'])+' '+str(journaldata[entry['syncstart']]['time'])+' | '+journaldata[entry['syncstart']]['action']+'  '+journaldata[entry['syncstart']]['event']+' | '+journaldata[entry['syncstart']]['sid']+' '+journaldata[entry['syncstart']]['user']+' | '+str(journaldata[entry['syncstart']]['index']))


# ------------------------------------------- #

##  PRINT RUNTIME

endtime = datetime.now()
print("\nruntime:")
print(endtime - starttime)
