#!/usr/bin/env python

import csv
import pprint
from datetime import datetime
import argparse
import os.path
import re
import collections
from devconf_talks import Canonical_Talk, Confirmed_Talk, Sched_Talk, Accepted_Talk, get_talk
#, .write_output

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
	help="csv file with accepted talks in planning sheet format")
ap.add_argument("-c", "--cfp", required=True, dest="cfp_talks_fn",
	help="csv file with talks from cfp.devconf.info")
ap.add_argument("-o", "--output", required=True, dest="output_fn",
	help="csv file output of talks that have been accepted and confirmed, uses sched format")
args = vars(ap.parse_args())


print("testing input params")
accepted_talks_fn = test_file(args["accepted_talks_fn"])
cfp_talks_fn = test_file(args["cfp_talks_fn"])
output_fn = args["output_fn"]

accepted_talks = Canonical_Talk.load_canonical_talks(accepted_talks_fn)
cfp_talks = Canonical_Talk.load_canonical_talks(cfp_talks_fn)
num_talks_in = 0
num_talks_included = 0
num_talks_with_starts = 0
for talk_id, talk in accepted_talks.items():
    num_talks_in += 1
    if talk.accepted and talk.confirmed and not talk.axed:
        num_talks_included += 1
        speakers = re.sub(remove_parens, "", talk.speakers)
        speakers = "; ".join([x.strip() for x in speakers.split(',')]).strip()
        talk.speakers = speakers
        talk.published = True
        talk.abstract = cfp_talks[talk_id].abstract if talk_id in cfp_talks.keys() is not None else ""
        if "start" in talk.keys() and talk.start is not '' and talk.start is not None:
            #sched_talks.append(Sched_Talk.to_sched(talk))
            num_talks_with_starts += 1
            sched_talks.append(talk)
        else:
            print("ID: {}, Title: {}, Accepted: {}, Confirmed: {}, Axed: {}, Start: {}".
                format(talk.id, talk.title, talk.accepted, talk.confirmed, talk.axed, talk.start))
    else:
        print("ID: {}, Title: {}, Accepted: {}, Confirmed: {}, Axed: {}".format(talk.id, talk.title, talk.accepted, talk.confirmed, talk.axed))

print("talks found = {}, talks selected = {}, talks with start times = {}".format(num_talks_in, num_talks_included, num_talks_with_starts))

Sched_Talk.write_output(sched_talks, output_fn)
