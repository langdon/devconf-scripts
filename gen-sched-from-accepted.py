#!/usr/bin/env python

import csv
import pprint
from datetime import datetime
import argparse
import os.path
import re
import collections
from devconf_talks import Canonical_Talk, Confirmed_Talk, Sched_Talk, get_talk, write_output

def test_file(fn):
    if not os.path.isfile(fn):
        print("{0} does not exist.".format(fn))
        exit()
    return fn
#def get_talk(talks, value, label = "ID"):
#    return next(item for item in talks if item[label] == str(value))

pp = pprint.PrettyPrinter(indent=4)
accepted_talks = []
confirmed_talks = []
sched_talks = []
remove_parens = re.compile(r"\(.*?\)", re.IGNORECASE)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--accepted", required=True, dest="accepted_talks_fn", 
	help="csv file with accepted talks in sched format")
ap.add_argument("-c", "--confirmed", required=True, dest="confirmed_talks_fn", 
	help="csv file with confirmed talks, format: ID,Track,Order,Title,Speaker,Confirmed,Constraints;" +
        "Only uses ID, Title, and Confirmed")
ap.add_argument("-o", "--output", required=True, dest="output_fn", 
	help="csv file output of talks that have been accepted and confirmed, uses sched format")
args = vars(ap.parse_args())


print("testing input params")
accepted_talks_fn = test_file(args["accepted_talks_fn"])
confirmed_talks_fn = test_file(args["confirmed_talks_fn"])
output_fn = args["output_fn"]

accepted_talks = Canonical_Talk.load_canonical_talks(accepted_talks_fn)
confirmed_talks = Canonical_Talk.load_canonical_talks(confirmed_talks_fn)

for c_talk_id in confirmed_talks:
    c_talk = confirmed_talks[c_talk_id]
    if c_talk.confirmed: 
        try:
            a_talk = accepted_talks[c_talk.id]
            if a_talk.title.strip() != c_talk.title.strip():
                print("Talk ID Mismatch: Confirmed Talk ID: {}, Title: '{}'; Accepted Talk Title: '{}'"
                    .format(c_talk.id, c_talk.title, a_talk.title))
        except (StopIteration, KeyError) as e:
            #talk not found in accepted set need to construct correct one
            a_talk = c_talk
        speakers = re.sub(remove_parens, "", a_talk.speakers)
        a_talk.speakers = speakers.replace(",", ";").strip()
        a_talk.published = True
        sched_talks.append(Sched_Talk.to_sched(a_talk))

write_output(sched_talks, output_fn, Sched_Talk.field_names)
