#!/usr/bin/env python

import csv
import pprint
from datetime import datetime
import argparse
import os.path
import re
import collections
from devconf_shared import Canonical_Talk, Confirmed_Talk, Sched_Talk, get_talk, write_output

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
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--scheduled", required=True, dest="scheduled_talks_fn", 
	help="csv file with scheduled talks in sched format")
ap.add_argument("-c", "--confirmed", required=True, dest="confirmed_talks_fn", 
	help="csv file with confirmed talks, format: ID,Track,Order,Title,Speaker,Confirmed,Constraints;" +
        "Only uses ID, Title, and Confirmed")
ap.add_argument("-o", "--output", required=True, dest="output_fn", 
	help="csv file output of talks that have problems")
ap.add_argument("--sched-format", action="store_true", dest="output_sched_format", 
        help="defaults to confirmed format, make this true to switch to sched")
args = vars(ap.parse_args())


print("testing input params")
scheduled_talks_fn = test_file(args["scheduled_talks_fn"])
confirmed_talks_fn = test_file(args["confirmed_talks_fn"])
output_fn = args["output_fn"]
output_sched_format = args["output_sched_format"]

all_set = {}
problems = []

# expected structure: ID, Title, Type/Track, Description, Speakers
#you must manually remove the trash lines from the top of the sched file
print("processing scheduled talks from " + scheduled_talks_fn)
with open(scheduled_talks_fn) as csvfile:
    reader = csv.DictReader(csvfile, delimiter='|', quotechar='~')
    tmp = list(reader)
    for talk in tmp:
        scheduled_talks[talk["ID"]] = Canonical_Talk.to_canonical_talk(talk)

#    print("scheduled_talks:")
#    pp.pprint(scheduled_talks)

#expected structure: ID, Track, Order, Title, Speaker, Confirmed, Constraints
print("processing confirmed talks from " + confirmed_talks_fn)
with open(confirmed_talks_fn) as csvfile:
#    my_fields = ["ID", "Track", "Order", "Title", "Speaker", "Confirmed", "Constraints"]
    reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
#    reader = csv.DictReader(csvfile, delimiter='~', quotechar="|")
    for row in reader:
        confirmed_talk = Canonical_Talk.to_canonical_talk(row)
        if confirmed_talk['confirmed']:
            print("Confirmed talk: has {}:\"{}\" been scheduled? ".format(confirmed_talk.id, confirmed_talk.title), end='')     
            #look for the talk in scheduled by id
            try:
                talk = scheduled_talks[confirmed_talk.id]  
                #talk = get_talk(scheduled_talks, row["ID"])
                if talk.title.strip() != confirmed_talk.title.strip():
                    print(" -- Talk ID Mismatch: Confirmed Talk ID: {}, Title: '{}'; Accepted Talk Title: '{}'"
                        .format(confirmed_talk.id, confirmed_talk.title, talk.title))
                    problems.append(confirmed_talk)
                else:
                    all_set[confirmed_talk.id] = {"scheduled" : talk, "confirmed" : confirmed_talk}
                    print("Yes: {}-{}".format(talk.start, talk.end))
                    scheduled_talks.pop(confirmed_talk.id)
            except (StopIteration, KeyError) as e:
                try:
                    #talk not found by id, check for it by title
                    talk = get_talk(scheduled_talks, confirmed_talk.title, "Title")
                    all_set[talk.id] = {"scheduled" : talk, "confirmed" : confirmed_talk}
                    print("Yes: {}-{}".format(talk.start, talk.end))
                    scheduled_talks.pop(talk.id)
                except (StopIteration, KeyError) as e:
                    #ok not found at all, let's report it
                    problems.append(confirmed_talk)
                    print(" -- Talk confirmed but not scheduled: Confirmed Talk ID: {}, Title: '{}'"
                        .format(confirmed_talk.id, confirmed_talk.title))

# this should be empty, else it means unconfirmed talks are scheduled
for talk_id, talk in scheduled_talks.items(): 
    problems.append(talk)

print("these talks are all set!")
for talk_id in all_set:
    talk = all_set[talk_id]["scheduled"]
    print("Talk: {}: \"{}\" at {}-{}".format(talk.id, talk.title, talk.start, talk.end))
print("these talks need to be fixed!")

problems_forprint = []
field_names = ""
if not output_sched_format:
    for talk in problems:
        problems_forprint.append(Confirmed_Talk.to_confirmed(talk))
    field_names = Confirmed_Talk.field_names
else: 
    for talk in problems:
        problems_forprint.append(Sched_Talk.to_sched(talk))
    field_names = Sched_Talk.field_names

write_output(problems_forprint, output_fn, field_names)
