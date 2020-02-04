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

#   last updated: 29/01/2020


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
    r"""(?P<action>\>|\<)"""
    r"""(?P<event>[^\s]*)"""
    r"""(?P<parameter>.*)\r"""
)
regex_select_allevents = r"""(?P<action>\.)(?P<event>[^\s]*)(?P<parameter>.*)\r"""
regex_select_stcstl = r"""(?P<action>\>|\<)(?P<event>STC:STL)\r"""
regex_select_stc = r"""(?P<action>\>|\<)(?P<event>STC)\r"""

# put the regex together. change the second part
regex = re.compile(regex_base + regex_select_alltransactions)

# grab session informations to assign user to sessionID, also get build version and the host....
regex_sid = re.compile(
    r"""(?P<sid>\$.[0-9a-fA-F]{7}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}).*\n\s\buser\=.(?P<user>\b.*\b).*\n\s\bbuild\=.(?P<build>\b.*\b.).*\n\s\bjournal\=.(?P<journal>\b.*\b).*\n\s\bhost\=(?P<host>.*.)\r"""
)

# grab all events/transaction and split into groups. !!! parameter currently always has to leading whitespaces!
# regex_allevents = re.compile(
#    r"""(?P<sid>\$[0-9a-fA-F]{8}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]{3}).(?P<action>\>|\<|\.)(?P<event>[^\s]*)(?P<parameter>.*)\r"""
# )
# grab only "save local before/after sync" events
# regex_stcstl = re.compile(
#    r"""(?P<sid>\$[0-9a-fA-F]{8}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]{3}).(?P<action>\>|\<)(?P<event>STC:STL)\r"""
# )

# grab only "save local before/after sync" events
# regex_stc = re.compile(
#    r"""(?P<sid>\$[0-9a-fA-F]{8}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]{3}).(?P<action>\>|\<)(?P<event>STC)\r"""
# )


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

# getting user sessiondata
sessiondata = regex_sid.finditer(wsjdata, re.MULTILINE)
# getting events (set regex above)
journaldata = regex.finditer(wsjdata)


##  processing data

# regex to dictionary
sessiondata = [dict(session.groupdict()) for session in sessiondata]
journaldata = [dict(entry.groupdict()) for entry in journaldata]

# assign user to entries
for session in sessiondata:
    for entry in journaldata:
        if entry["sid"] == session["sid"]:
            entry["user"] = session["user"]

# finessing the data
for session in sessiondata:
    session["date"] = datetime.strptime(session["date"], "%Y-%m-%d").date()
    session["time"] = datetime.strptime(session["time"], "%H:%M:%S").time()
for entry in journaldata:
    entry["date"] = datetime.strptime(entry["date"], "%Y-%m-%d").date()
    entry["time"] = datetime.strptime(entry["time"], "%H:%M:%S").time()

    if entry["parameter"]:
        entry["parameter"] = entry["parameter"][2:]


# ------------------------------------------- #


##  DELIVERING RESULTS

for session in sessiondata[-3:]:
    print(session)

print("---")

for entry in journaldata[-100:-95]:  # [-10:] last 10 entries
    print(entry)

# print([list(i) for i in journaldata])


# ------------------------------------------- #

##  PRINT RUNTIME

endtime = datetime.now()
print("\nruntime:")
print(endtime - starttime)
