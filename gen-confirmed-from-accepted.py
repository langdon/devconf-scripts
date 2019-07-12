#!/usr/bin/env python
"""
You can use this script to take all accepted from the cfp tool and all 
"to confirm" talks from Langdon's original DevConf.US Planning spreadsheet(s) 
and spit out a merged set of "to confirm" talks."
"""

import csv
import pprint
from datetime import datetime
import argparse
import os.path
import re
import collections
from devconf_talks import Canonical_Talk, Confirmed_Talk, Sched_Talk, get_talk

def test_file(fn):
    if not os.path.isfile(fn):
        print("{0} does not exist.".format(fn))
        exit()
    return fn

pp = pprint.PrettyPrinter(indent=4)
scheduled_talks = {}
confirmed_talks = []
remove_parens = re.compile(r"\(.*?\)", re.IGNORECASE)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("-a", "--accepted", required=True, dest="accepted_talks_fn", 
	help="csv file with accepted talk in cfp tool format (should be very similar to sched)")
ap.add_argument("-c", "--confirmed", required=True, dest="confirmed_talks_fn", 
	help="csv file with confirmed talks, format: ID,Track,Order,Title,Speaker,Confirmed,Constraints;" +
        "Only uses ID, Title, and Confirmed")
ap.add_argument("-o", "--output", required=True, dest="output_fn", 
	help="csv file output of talks that need or have confirmation")
args = vars(ap.parse_args())


print("testing input params")
accepted_talks_fn = test_file(args["accepted_talks_fn"])
confirmed_talks_fn = test_file(args["confirmed_talks_fn"])
output_fn = args["output_fn"]

accepted_talks = {}
confirmed_talks = {}
merged_talks = {}

# expected structure: ID, Title, Type/Track, Description, Speakers
#you must manually remove the trash lines from the top of the sched file
accepted_talks = Canonical_Talk.load_canonical_talks(accepted_talks_fn)
confirmed_talks = Canonical_Talk.load_canonical_talks(confirmed_talks_fn)

for talk_id, talk in accepted_talks.items():
    if not talk_id in confirmed_talks:
        merged_talks[talk_id] = talk

Confirmed_Talk.write_output(merged_talks, output_fn)

