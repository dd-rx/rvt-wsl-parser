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

#   last updated: m.wild 16/02/2020
#   ^ this header may not be removed - only extended.


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
import csv



## FUNCTIONS


def RegexToDict(_input):
    _dict = [dict(_session.groupdict()) for _session in _input]
    del _input
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


def DeliverSessionSummary(_sessiondata):
    # if _v == 3:
    #     for _session in _sessiondata:
    #         print(
    #             f'{_session["date"]}, {_session["time"]} | {_session["sid"]} {_session["user"]} - {_session["build"]} {_session["host"]}'
    #         )
    # elif _v == 2:
    #     for _session in _sessiondata:  # [-10:] last 10 entries
    #         print(
    #             str(_session["date"])
    #             + ", "
    #             + str(_session["time"])
    #             + " | "
    #             + _session["sid"]
    #             + " "
    #             + _session["user"]
    #             + " - "
    #             + _session["build"]
    #             + " "
    #             + _session["host"]
    #         )
    print("SESSIONS:")
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

    if crashes:
        print("CRASHES:")
        for _crash in crashes:
            print(
                str(journaldata[_crash["crash"]]["date"])
                + ", "
                + str(journaldata[_crash["crash"]]["time"])
                + " | "
                + journaldata[_crash["crash"]]["sid"]
                + " "
                + journaldata[_crash["crash"]]["user"]
            )

    if reconnects:
        print("RECONNECTS:")
        for _reconnect in reconnects:
            print(
                str(journaldata[_reconnect["reconnect"]]["date"])
                + ", "
                + str(journaldata[_reconnect["reconnect"]]["time"])
                + " | "
                + journaldata[_reconnect["reconnect"]]["sid"]
                + " "
                + journaldata[_reconnect["reconnect"]]["user"]
            )
    del _sessiondata


def DeliverSessionDuration():
    # this can be messy if you have users computer go to standby - revit then re-opens a session with the same sid
    for _sessionmetaindex, _sessionmeta in enumerate(sessions):
        if _sessionmeta["sessionend"]:

            # for readability, create a shorthandle for the data in sessiondata and journaldata
            _sessiondatalink = sessiondata[sessions[_sessionmetaindex]["sessionstart"]]
            _journaldatalink = journaldata[sessions[_sessionmetaindex]["sessionend"]]

            # calculate session duration
            _sessionduration = CalculateDuration(_sessiondatalink, _journaldatalink)

            print(
                f'{_sessiondatalink["date"]} '
                f'{_sessiondatalink["time"]} '
                f'{_sessiondatalink["sid"]} '
                f'{_sessiondatalink["user"]}  |  '
                f"{_sessionduration}  |  "
                f'{_journaldatalink["date"]} '
                f'{_journaldatalink["time"]} '
                f'{_journaldatalink["sid"]} '
                f'{_journaldatalink["user"]}'
            )

            # housekeeping
            del _sessiondatalink, _journaldatalink, _sessionduration

        elif not _sessionmeta["sessionend"]:
            _unfinishedsessionwarning = 1

            # for readability, create a shorthandle for the data in sessiondata
            _sessiondatalink = sessiondata[sessions[_sessionmetaindex]["sessionstart"]]

            # for _crash in crashes:
            #     if journaldata[_crash['crash']]['sid'] == _sessiondatalink['sid']:
            #         pass

            print(
                f'{_sessiondatalink["date"]} '
                f'{_sessiondatalink["time"]} '
                f'{_sessiondatalink["sid"]} '
                f'{_sessiondatalink["user"]}  |  '
                f"no endpoint found..?!"
            )

            # housekeeping
            del _sessiondatalink

    if _unfinishedsessionwarning:
        print(f"\nsessions without endpoint are either still active")
        print(f"or client computer went into standby mode and came back")
        print(f"in which case revit opens a new session with the same sid")

        # housekeeping
        del _unfinishedsessionwarning

    del _sessionmetaindex, _sessionmeta



def ExportCSV(_input,_filename,_delimiter=','):

    _filename = str(datetime.today().strftime('%Y%m%d'))+'_'+_filename+'.csv'

    if _input == 'worksharing':
        with open(_filename, mode='w', newline='') as _tmpcsv:
            _header = ['index', 'sid', 'user', 'date', 'time', 'action', 'event', 'parameter']
            _export = csv.DictWriter(_tmpcsv, fieldnames=_header, delimiter=_delimiter)

            _export.writeheader()

            for _entry in journaldata:
                _export.writerow(_entry)

        del _tmpcsv, _header, _export, _entry

    elif _input == 'session':
        #TODO add sessionduration
        with open(_filename, mode='w', newline='') as _tmpcsv:
            _header = ['sid', 'user', 'date', 'time', 'build', 'host', 'journal']
            _export = csv.DictWriter(_tmpcsv, fieldnames=_header, delimiter=_delimiter)

            _export.writeheader()

            for _session in sessiondata:
                _export.writerow(_session)

        del _tmpcsv, _header, _export, _session

    elif _input == 'sync':
        pass

    #_input = 0
    #del __data, _filename, delimiter




# ------------------------------------------- #

##  SET UP TIMER

starttime = datetime.now()


# ------------------------------------------- #

##  REGEX
# !!! gingercareful: depending on python implementation named groups are defined by ?<foo> ?P<foo> or maybe others. assigned as raw bytes.


# trying to make the regex modular...
# regex_base is reused for all patterns. gets sessionid date time
regex_base = r"""(?P<sid>\$[0-9a-fA-F]{8}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]{3})."""

regex_allevents = r"""(?P<action>\>|\<|\.)(?P<event>[^\s]*)(?P<parameter>.*)\r"""

regex = re.compile(regex_base + regex_allevents)

# grab session informations to assign user to sessionID, also get build version and the host....
regex_sessiondata = re.compile(
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
sessiondata = regex_sessiondata.finditer(wsjdata, re.MULTILINE)
# getting events (set regex above)
journaldata = regex.finditer(wsjdata)

# housekeeping
del regex
del regex_sessiondata
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

#housekeeping
del _session
del _entry

# lists of connections
syncstocentral = []
savelocalbeforesync = []  #
crashes = []
reconnects = []
sessions = []


# finessing the journaldata
for _index, _entry in enumerate(journaldata):

    # date/time formatting
    _entry["date"], _entry["time"] = FormatDateTime(_entry["date"], _entry["time"])

    # assign index
    _entry["index"] = _index

    # clean up two leading spaces in parameter
    if _entry["parameter"]:
        _entry["parameter"] = _entry["parameter"][2:]

    # --- # going for the different events

    # STC:RL:CFV | centralfile generation
    if _entry["event"] == "STC:RL:CFV":
        pass
        # print(_entry['parameter'][8:])

    # STC | get sync events
    elif _entry["event"] == "STC":
        if _entry["action"] == ">":
            syncstocentral.append({"syncstart": _index, "syncend": ""})
            # break
        # get end of sync event | #TODO how to detect unfinished syncs??
        elif _entry["action"] == "<":
            # TODO how stupid is it to assume there is only one open syncronisation per user so i can stop matching after first hmatch when going thru the list backwards..?!
            for _sync in syncstocentral[::-1]:
                if (
                    not _sync["syncend"]
                    and journaldata[_sync["syncstart"]]["sid"] == _entry["sid"]
                ):
                    _sync["syncend"] = _index

                    # calculate syncduration
                    _sync["syncduration"] = CalculateDuration(
                        journaldata[_sync["syncstart"]], journaldata[_sync["syncend"]]
                    )

                    # break
    # Session | get end of session
    elif _entry["event"] == "Session":
        if _entry["action"] == ">":
            for _sessionindex, _session in enumerate(sessiondata):
                if _entry["sid"] == _session["sid"]:
                    sessions.append({"sessionstart": _sessionindex, "sessionend": ""})
        if _entry["action"] == "<":
            for _sessionmeta in sessions[::-1]:
                if sessiondata[_sessionmeta["sessionstart"]]["sid"] == _entry["sid"]:
                    _sessionmeta["sessionend"] = _index
            #print(sessions)

    # Crah |report crash
    elif _entry["event"] == "Crash":
        if _entry["action"] == ">":
            crashes.append({"crash": _index})
    # ReConnectInMiddle | get reconnects
    elif _entry["event"] == "ReConnectInMiddle":
        if _entry["action"] == ">":
            reconnects.append({"reconnect": _index})
            print("RECONNECT")

    # sceleton
    # elif _entry["event"] == "foo":
    #     if _entry["action"] == ">":
    #         pass
    #     elif _enty["action"] == "<":
    #         pass

    # ^^^ # going for the different events

# ------------------------------------------- #

##  DELIVERING RESULTS


#DeliverSessionDuration()

#DeliverSessionSummary(sessiondata)

ExportCSV('worksharing','worksharing')
ExportCSV('session','sessions')

# print("------------------")
# for _sessionmetaindex, _sessionmeta in enumerate(sessions):
#     print(
#         f'{sessiondata[sessions[_sessionmetaindex]["sessionstart"]]["user"]}{journaldata[sessions[_sessionmetaindex]["sessionend"]]["user"]}'
#     )


print("------------------")

# ------------------------------------------- #
# housekeeping
del journaldata
#del sessiondata

##  PRINT RUNTIME

endtime = datetime.now()
print("\nruntime:")
print(endtime - starttime)
