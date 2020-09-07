#!/usr/bin/env python
"""
You can use this script to count the number of "wearables" and sizes required
by speakers who have been scheduled to speak."
"""

import csv
import pprint
from datetime import datetime
import argparse
import os.path
import re
import collections
from devconf_speakers import Canonical_Speaker, Sched_Speaker, CFP_Speaker

def test_file(fn):
    if not os.path.isfile(fn):
        print("{0} does not exist.".format(fn))
        exit()
    return fn
#def get_talk(talks, value, label = "ID"):
#    return next(item for item in talks if item[label] == str(value))

pp = pprint.PrettyPrinter(indent=4)
accepted_speakers = []
sched_speakers = []

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cfp", required=True, dest="cfp_speakers_fn", 
	help="csv file with speakers in cfp format")
ap.add_argument("-s", "--scheduled", required=True, dest="sched_speakers_fn", 
	help="csv file with speakers from sched, uses their format")
#ap.add_argument("-o", "--output", required=True, dest="output_fn", 
#	help="csv file output of speakers in the sched format, will not overwrite sched data")
args = vars(ap.parse_args())


print("testing input params")
cfp_speakers_fn = test_file(args["cfp_speakers_fn"])
sched_speakers_fn = test_file(args["sched_speakers_fn"])
#output_fn = args["output_fn"]

sched_speakers = {}
with open(sched_speakers_fn) as csvfile:
    reader = csv.DictReader(csvfile)
    tmp = list(reader)
    for speaker in tmp:
        speaker = Sched_Speaker.to_canonical_speaker(speaker)
        #if speaker.name.strip() and speaker.email.strip():
        sched_speakers[speaker.email] = speaker 

cfp_speakers = {}
with open(cfp_speakers_fn) as csvfile:
    reader = csv.DictReader(csvfile)
    tmp = list(reader)
    for speaker in tmp:
        #loop for all speakers in set
        cfp_speakers.update(CFP_Speaker.to_canonical_speaker(speaker))

sizes = {}
for email, speaker in sched_speakers.items():
    try:
        cfp_speaker = cfp_speakers[email]
        size_combo = cfp_speaker.wearable_gender + "-" + cfp_speaker.wearable_size 
        if size_combo in sizes:
            sizes[size_combo] += 1
        else:
            sizes[size_combo] = 1
    except KeyError as e:
        print("email address: '{}' and name: '{}' not found in the accepted speaker list which is weird".format(email, speaker.name))

pp.pprint(sizes)
