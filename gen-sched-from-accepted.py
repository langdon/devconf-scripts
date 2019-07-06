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
#def get_talk(talks, value, label = "ID"):
#    return next(item for item in talks if item[label] == str(value))

pp = pprint.PrettyPrinter(indent=4)
accepted_talks = []
confirmed_talks = []
sched_talks = []
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

# expected structure: ID, Title, Type/Track, Description, Speakers
#print("processing accepted talks from " + accepted_talks_fn)
#with open(accepted_talks_fn) as csvfile:
#    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
#    accepted_talks = list(reader)
#pp.pprint(accepted_talks)
#expected structure: ID, Track, Order, Title, Speaker, Confirmed, Constraints
#print("processing confirmed talks from " + confirmed_talks_fn)
#with open(confirmed_talks_fn) as csvfile:
#    reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
#    tmp = list(reader)
    #pp.pprint(tmp)


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
            #  Canonical_Talk()
            # a_talk.id = c_talk.id
            # a_talk.title = c_talk.title
            # a_talk.track = c_talk.track
            # a_talk.abstract = c_talk.abstract
            # a_talk.id = c_talk.id
            # a_talk.id = c_talk.id
            # talk["ID"] = row["ID"]
            # talk["Title"] = row["Title"]
            # talk["Type/Track"] = track_lookup[row["Track"]]
            # talk["Description"] = row["Abstract"]
            # talk["Speakers"] = str(row["Speaker"])
        speakers = re.sub(remove_parens, "", a_talk.speakers)
        a_talk.speakers = speakers.replace(",", ";").strip()
        a_talk.published = True
        sched_talks.append(Sched_Talk.to_sched(a_talk))

"""
confirmed_talks = Canonical_Talk.load_canonical_talks(confirmed_talks_fn)

with open(confirmed_talks_fn) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
#    reader = csv.DictReader(csvfile, delimiter='~', quotechar="|")
    for row in reader:
        confirmed_talk = Canonical_Talk.to_canonical_talk(row)
        if confirmed_talk.confirmed: 
#        if row["Confirmed"] == "Yes":
            print("Confirmed talk, looking up " + row["ID"] + " with title: " + row["Title"])
            try:
                talk = get_talk(accepted_talks, row["ID"])
                if talk["Title"].strip() != row["Title"].strip():
                    print("Talk ID Mismatch: Confirmed Talk ID: {}, Title: '{}'; Accepted Talk Title: '{}'"
                        .format(row["ID"], row["Title"], talk["Title"]))
            except StopIteration as e:
                #talk not found in accepted set need to construct correct one
                talk = collections.OrderedDict()
                talk["ID"] = row["ID"]
                talk["Title"] = row["Title"]
                talk["Type/Track"] = track_lookup[row["Track"]]
                talk["Description"] = row["Abstract"]
                talk["Speakers"] = str(row["Speaker"])
            speakers = re.sub(remove_parens, "", talk["Speakers"])
            talk["Speakers"] = speakers.replace(",", ";")
            talk["Published?"] = "Y"
            sched_talks.append(talk)

#pp.pprint(sched_talks)

#my_fields = 

with open(output_fn, 'w') as csvfile:
    out_writer = csv.DictWriter(csvfile, fieldnames=Sched_Talk.field_names, quoting=csv.QUOTE_ALL)
#    for i in range(1,8):
#        out_writer.writerow("")
    out_writer.writeheader()
    out_writer.writerows(sched_talks)
"""

write_output(sched_talks, output_fn, Sched_Talk.field_names)
