#   created 13/01/2020 | ddrx:johndoe
#   last updated 26/01/2020
# 	pyCharm | venv | black

#
#   "We interrupt this program to annoy you
#   and make things generally more irritating."
#                              -Monty Python's Flying Circus
#


#   this is a parser vor revit worksharingjournals (*.slog)

#   !!! opening UCS-2-LE .slog as UTF-16-LE ... *duck&run*

##imports
import re
import codecs  # codecs needed for python 2
from datetime import datetime

##regex !!! gingercarefull young padawan: depending on python implementation named groups are defined by ?<foo> ?P<foo> or maybe others. assigned as raw bytes.

# grab session informations to assign user to sessionID, also get build version and the host....
regex_sid = re.compile(
    r"""(?P<sid>\$.[0-9a-fA-F]{7}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}).*\n\s\buser\=.(?P<user>\b.*\b).*\n\s\bbuild\=.(?P<build>\b.*\b.).*\n\s\bjournal\=.(?P<journal>\b.*\b).*\n\s\bhost\=.(?P<host>.*.)"""
)

# grab all events/transaction and split into groups. !!! parameter currently always has to leading whitespaces!
regex_allevents = re.compile(
    r"""(?P<sid>\$[0-9a-fA-F]{8}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]{3}).(?P<type>\>|\<|\.)(?P<event>[^\s]*)(?P<parameter>.*)\r"""
)
# grab only "save local before/after sync" events
regex_stcstl = re.compile(
    r"""(?P<sid>\$[0-9a-fA-F]{8}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]{3}).(?P<type>\>|\<)(?P<event>STC:STL)\r"""
)

# grab only "save local before/after sync" events
regex_stc = re.compile(
    r"""(?P<sid>\$[0-9a-fA-F]{8}).(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}).(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]{3}).(?P<type>\>|\<)(?P<event>STC)\r"""
)

# set up timer
starttime = datetime.now()


########################################

##accuisition

# read WorkSharingJournal
wsj = codecs.open(
    r"""#filepath""",
    "r",
    encoding="utf-16",
)
wsjdata = wsj.read()
wsj.close()

# getting user sessiondata
sessiondata = regex_sid.findall(wsjdata, re.MULTILINE)
# getting events (see above)
journaldatatuples = regex_stc.findall(wsjdata)

## processing

# tuple to list
journaldata = [list(tuple) for tuple in journaldatatuples]

# replace sessionid with user | #TODO to be rewritten...but works.
for session in sessiondata:
    for event in journaldata:
        if event[0] == session[0]:
            event[0] = event[0].replace(event[0], session[3])
# sanitized date/time | #TODO refactoring needed check: https://www.geeksforgeeks.org/python-iterate-multiple-lists-simultaneously/
for event in journaldata:
    event[1] = datetime.strptime(event[1], "%Y-%m-%d").date()
    event[2] = datetime.strptime(event[2], "%H:%M:%S").time()


#########################################

## delivering

for session in sessiondata:
    print(
        session[0]
        + " "
        + session[3]
        + " "
        + session[1]
        + " "
        + session[2]
        + " "
        + session[4]
    )

print("---")

for event in journaldata[-10:]:  # [-10:] last 10 entries
    print(event)

# print([list(i) for i in journaldata])

# print runtime
print("\nruntime:")
endtime = datetime.now()
print(endtime - starttime)
