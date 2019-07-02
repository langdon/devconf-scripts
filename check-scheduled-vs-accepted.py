#!/usr/bin/env python

import csv
import pprint
from datetime import datetime
import argparse
import os.path
import re
import collections

def test_file(fn):
    if not os.path.isfile(fn):
        print("{0} does not exist.".format(fn))
        exit()
    return fn
def get_talk(talks, value, label = "ID"):
    return next(item for item in talks if item[label] == str(value))

pp = pprint.PrettyPrinter(indent=4)
scheduled_talks = []
confirmed_talks = []
remove_parens = re.compile(r"\(.*?\)", re.IGNORECASE)
track_lookup = {
    "AD&C": "Application Development & Containerization",
    "B&RCI": "Building and Running Cloud Infra",
    "ESQ": "Ensuring Software Quality",
    "ML": "ML: Privacy & Big Data",
    "OSP": "Open Source & Process",
    "S": "Serverless",
    "SE&H": "Systems Engineering & Hardware",
    "UX": "User Experience in OS"}

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--scheduled", required=True, dest="scheduled_talks_fn", 
	help="csv file with scheduled talks in sched format")
ap.add_argument("-c", "--confirmed", required=True, dest="confirmed_talks_fn", 
	help="csv file with confirmed talks, format: ID,Track,Order,Title,Speaker,Confirmed,Constraints;" +
        "Only uses ID, Title, and Confirmed")
ap.add_argument("-o", "--output", required=True, dest="output_fn", 
	help="csv file output of talks that have problems")
args = vars(ap.parse_args())


print("testing input params")
scheduled_talks_fn = test_file(args["scheduled_talks_fn"])
confirmed_talks_fn = test_file(args["confirmed_talks_fn"])
output_fn = args["output_fn"]

# expected structure: ID, Title, Type/Track, Description, Speakers
print("processing scheduled talks from " + scheduled_talks_fn)
with open(scheduled_talks_fn) as csvfile:
#    reader = csv.reader(csvfile)
#    for i in range(6): #skip first 7 rows
#        csvfile.readline()
#    useful_lines = csvfile.readline() # headers
#    csvfile.readline() # trash
#    useful_lines = useful_lines + csvfile.read()

#    print("useful lines:")
#    pp.pprint(useful_lines)

#    reader = csv.DictReader(useful_lines, delimiter='|', quotechar='~')
    reader = csv.DictReader(csvfile, delimiter='|', quotechar='~')
    scheduled_talks = list(reader)

#    print("scheduled_talks:")
#    pp.pprint(scheduled_talks)

#expected structure: ID, Track, Order, Title, Speaker, Confirmed, Constraints
print("processing confirmed talks from " + confirmed_talks_fn)
#with open(confirmed_talks_fn) as csvfile:
#    my_fields = ["ID", "Track", "Order", "Title", "Speaker", "Confirmed", "Constraints"]
#    reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
#    tmp = list(reader)
#    #pp.pprint(tmp)

all_set = {}
problems = []
with open(confirmed_talks_fn) as csvfile:
    my_fields = ["ID", "Track", "Order", "Title", "Speaker", "Confirmed", "Constraints"]
    reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
#    reader = csv.DictReader(csvfile, delimiter='~', quotechar="|")
    for row in reader:
        if row["Confirmed"] == "Yes":
            print("Confirmed talk: has {}:\"{}\" been scheduled? ".format(row["ID"], row["Title"]), end='')
            try:
                talk = get_talk(scheduled_talks, row["ID"])
                if talk["Title"].strip() != row["Title"].strip():
                    print(" -- Talk ID Mismatch: Confirmed Talk ID: {}, Title: '{}'; Accepted Talk Title: '{}'"
                        .format(row["ID"], row["Title"], talk["Title"]))
                    problems.append(row)
                else:
                    all_set[row["ID"]] = {"scheduled" : talk, "confirmed" : row}
                    print("Yes: {}-{}".format(talk["Start Date & Time"], talk["End Date & Time"]))
            except StopIteration as e:
                try:
                    #talk not found by id, check for it by title
                    talk = get_talk(scheduled_talks, row["Title"], "Title")
                    all_set[row["ID"]] = {"scheduled" : talk, "confirmed" : row}
                    print("Yes: {}-{}".format(talk["Start Date & Time"], talk["End Date & Time"]))
                except StopIteration as e:
                    #ok not found at all, let's report it
                    problems.append(row)
                    print(" -- Talk confirmed but not scheduled: Confirmed Talk ID: {}, Title: '{}'"
                        .format(row["ID"], row["Title"]))
print("these talks are all set!")
for talk_id in all_set:
    talk = all_set[talk_id]["scheduled"]
    print("Talk: {}: \"{}\" at {}-{}".format(talk["ID"], talk["Title"], talk["Start Date & Time"], talk["End Date & Time"]))
print("these talks need to be fixed!")
for talk in problems:
    #talk = problems.[talk_id]
    print("Confirmed talk: {}: \"{}\" (Track: {}:{})".format(talk["ID"], talk["Title"], talk["Track"], track_lookup[talk["Track"]]))
    #pp.pprint(talk) 

my_fields = ["ID", "Track", "Order", "Title", "Speaker", "Confirmed", "Constraints", "Abstract"]
with open(output_fn, 'w') as csvfile:
    out_writer = csv.DictWriter(csvfile, fieldnames=my_fields, quoting=csv.QUOTE_ALL)
    out_writer.writeheader()
    out_writer.writerows(problems)

