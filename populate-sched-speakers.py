import csv
import pprint
from datetime import datetime
import argparse
import os.path
import re
import collections
from devconf_speakers import Canonical_Speaker, Sched_Speaker, CFP_Speaker, CFP_App_Speaker

def test_file(fn):
    if not os.path.isfile(fn):
        print("{0} does not exist.".format(fn))
        exit()
    return fn
#def get_talk(talks, value, label = "ID"):
#    return next(item for item in talks if item[label] == str(value))

FIRST_LOAD = True
pp = pprint.PrettyPrinter(indent=4)
accepted_speakers = []
sched_speakers = []

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--accepted", required=True, dest="accepted_speakers_fn",
	help="csv file with accepted speakers in cfp format")
ap.add_argument("-s", "--sched", required=False, dest="sched_speakers_fn",
	help="csv file with speakers from sched, uses their format")
ap.add_argument("-o", "--output", required=True, dest="output_fn",
	help="csv file output of speakers in the sched format, will not overwrite sched data")
args = vars(ap.parse_args())


print("testing input params")
accepted_speakers_fn = test_file(args["accepted_speakers_fn"])
if args["sched_speakers_fn"]:
    sched_speakers_fn = test_file(args["sched_speakers_fn"])
    FIRST_LOAD = False
else:
    FIRST_LOAD = True
output_fn = args["output_fn"]

sched_speakers = {}
if FIRST_LOAD:
    accepted_speakers = {}
    with open(accepted_speakers_fn) as csvfile:
        reader = csv.DictReader(csvfile)
        tmp = list(reader)
        for speaker in tmp:
            #loop for all speakers in set
            speaker = CFP_App_Speaker.to_canonical_speaker(speaker)
            sched_speakers[speaker.email] = speaker

else:
    with open(sched_speakers_fn) as csvfile:
        reader = csv.DictReader(csvfile)
        tmp = list(reader)
        for speaker in tmp:
            speaker = Sched_Speaker.to_canonical_speaker(speaker)
            #if speaker.name.strip() and speaker.email.strip():
            sched_speakers[speaker.email] = speaker

    accepted_speakers = {}
    with open(accepted_speakers_fn) as csvfile:
        reader = csv.DictReader(csvfile)
        tmp = list(reader)
        for speaker in tmp:
            #loop for all speakers in set
            accepted_speakers.update(CFP_Speaker.to_canonical_speaker(speaker))

    modified_speakers = {}
    for email, speaker in sched_speakers.items():
        try:
            accepted_speaker = accepted_speakers[email]
            modified = False
            for key in speaker:
                if not speaker[key].strip() and key in accepted_speaker.keys():
                    speaker[key] = accepted_speaker[key]
                    modified = True
            if modified:
                modified_speakers[speaker.email] = speaker
        except KeyError as e:
            print("email address: '{}' and name: '{}' not found in the accepted speaker list which is weird".format(email, speaker.name))
    pp.pprint(modified_speakers)

Sched_Speaker.write_output(sched_speakers, output_fn)

"""
    def load_canonical_speakers(fn, **kwargs):
        speakers = {}
        with open(fn) as csvfile:
            reader = csv.DictReader(csvfile, **kwargs)
            tmp = list(reader)
            for speaker in tmp:
                speakers[speaker["ID"]] = Canonical_Speaker.to_canonical_speaker(speaker)
                Sched_Speaker.to_canonical_speaker(messy_speaker)
        return speakers


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

write_output(sched_talks, output_fn, Sched_Talk.field_names)
"""
