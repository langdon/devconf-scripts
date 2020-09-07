#!/usr/bin/env python

import csv
import pprint
from datetime import datetime
import argparse
import os.path
import re
import collections
from devconf_talks import Canonical_Talk, Sched_Talk
from devconf_speakers import  Sched_Speaker, Canonical_Speaker

def test_file(fn):
    if not os.path.isfile(fn):
        print("{0} does not exist.".format(fn))
        exit()
    return fn
#def get_talk(talks, value, label = "ID"):
#    return next(item for item in talks if item[label] == str(value))

pp = pprint.PrettyPrinter(indent=4)
talks = []
sched_speakers = []
remove_parens = re.compile(r"\(.*?\)", re.IGNORECASE)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--talks", required=True, dest="sched_talks_fn",
	help="csv file with talk in sched format")
ap.add_argument("-s", "--speakers", required=True, dest="speakers_fn",
	help="csv file with speakers in sched format")
ap.add_argument("-o", "--output", required=True, dest="output_fn",
	help="csv file speakers actually giving talks in sched format")
args = vars(ap.parse_args())

print("testing input params")
sched_talks_fn = test_file(args["sched_talks_fn"])
sched_speakers_fn = test_file(args["speakers_fn"])
output_fn = args["output_fn"]

talks = Canonical_Talk.load_canonical_talks(sched_talks_fn)
speakers = Canonical_Speaker.load_canonical_speakers(sched_speakers_fn)

speakers_with_talks= ""

for talk_id, talk in talks.items():
    speakers_with_talks += "; " + talk.speakers

actual_speakers = {}
for speaker_id, speaker in speakers.items():
    if speaker.name in speakers_with_talks:
        actual_speakers[speaker.email] = speaker

Sched_Speaker.write_output(actual_speakers, output_fn)
