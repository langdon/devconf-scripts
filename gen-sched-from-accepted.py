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
#ap.add_argument("-i", "--input", action="store_true", dest="send_email", 
#	help="actually send emails")
#ap.add_argument("-d", "--debug", action="store_true", dest="debug_email", 
#	help="send emails to debug address")
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
print("processing accepted talks from " + accepted_talks_fn)
with open(accepted_talks_fn) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    accepted_talks = list(reader)
#pp.pprint(accepted_talks)

#expected structure: ID, Track, Order, Title, Speaker, Confirmed, Constraints
print("processing confirmed talks from " + confirmed_talks_fn)
with open(confirmed_talks_fn) as csvfile:
    my_fields = ["ID", "Track", "Order", "Title", "Speaker", "Confirmed", "Constraints"]
    reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
    tmp = list(reader)
    #pp.pprint(tmp)

with open(confirmed_talks_fn) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
#    reader = csv.DictReader(csvfile, delimiter='~', quotechar="|")
    for row in reader:
        if row["Confirmed"] == "Yes":
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

my_fields = ["ID", "Title", "Published?", "Start Date & Time", "End Date & Time", "Type/Track", "Sub-type",	"Capacity", "Description", "Speakers"]
with open(output_fn, 'w') as csvfile:
    out_writer = csv.DictWriter(csvfile, fieldnames=my_fields, quoting=csv.QUOTE_ALL)
#    for i in range(1,8):
#        out_writer.writerow("")
    out_writer.writeheader()
    out_writer.writerows(sched_talks)

"""
for talk in confirmed_talks
    for row in reader:
        accepted_talks = {  
            ID	Title	Type/Track	Description	Speakers

            "id" : row["ID"],
            "title" : row["Title"],
            "email" : row['Email Address'], 
            "name" : row['Primary Profile Name'],
            "picture" : row["Primary Profile Picture"],
            "profile_short_description" : row["Primary Profile Short Description"],
            "biography" : row["Primary Profile Biography"],
            "organization" : row["Primary Profile Organization"],
            "community" : row["Primary Profile Community"],
            "wearable_size" : row["Primary Profile Wearable Size Preference"],
            "wearable_size_gender" : row["Primary Profile Wearable Size Gender Preference"],
            "twitter_url" : row["Primary Profile Twitter URL"],
            "github_url" : row["Primary Profile GitHub URL"],
            "website_url" : row["Primary Profile Website URL"],
            "agreed" : row["I and all other secondary participants have read, and agree with the DevConf participation agreement"]
            }


print("processing sched-titles.csv")
#devconfus2018-event-export-2018-07-06-13-26-33.csv
with open('./sched-titles.csv') as csvfile:
    selected_reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in selected_reader:
        title = row["Title"].strip()
        for speaker in row["Speakers"].split(";"):
            speaker = speaker.strip()
            sched_talks[title] = {"name" : speaker}
            sched_talks[title].update({"title" : title})
            sched_talks[title].update({"published" : True if (row["Published?"] == 'Y') else False})

id	status
1	Submitted
2	Voting
3	Voting Complete
4	Proposed Selected
5	Author Contacted
6	Author Accepted
7	Scheduled
8	Author Declined
9	Unknown
select_stmt = open('./select-stmt.sql', 'w')
select_stmt.write("SELECT * from \"Papers\" WHERE id in (")

open('./not-scheduled-update-stmts.sql', 'w').close()
update_stmts = open('./not-scheduled-update-stmts.sql', 'a')

print("checking status of sched talk in db list")
#export of users_titles_by_status view
with open('./users_titles_by_status.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        title = row["title"].strip()
        db_titles[title] = {"title" : title}
        db_titles[title].update({"name" : row["name"]})
        db_titles[title].update({"email" : row["email"]})
        db_titles[title].update({"status" : row["status"]})
        db_titles[title].update({"status_id" : int(row["status_id"])})
        db_titles[title].update({"paper_id" : int(row["paper_id"])})
        db_titles[title].update({"user_id" : int(row["user_id"])})

        try:
            sched_talk = sched_talks.pop(title)
            if (db_titles[title]["status_id"] != 7):
                conflicts[title] = db_titles[title]
                conflicts[title].update({"reason" : "talk is in sched but status is not 7"})
                update_stmts.write("UPDATE \"Papers\" SET statusid = 7 where id = {0};\n".format(db_titles[title]["paper_id"]))
                select_stmt.write("{0},".format(db_titles[title]["paper_id"]))
        except:
            if (db_titles[title]["status_id"] == 5 or
                db_titles[title]["status_id"] == 6 or
                db_titles[title]["status_id"] == 7 or
                db_titles[title]["status_id"] == 9):
                conflicts[title] = db_titles[title]
                conflicts[title].update({"reason" : "status in db is 5,6,7,9 but sched doesn't have it"})

for title, sched_talk in sched_talks.items():
    print(sched_talk)         

select_stmt.write(")")
select_stmt.close()
update_stmts.close()

print("writing conflicts file")
my_fields = ["paper_id","email","name","title","status","user_id","status_id", "reason"]
with open('./conflicts.csv', 'w') as csvfile:
    out_writer = csv.DictWriter(csvfile, fieldnames=my_fields)
    for title, out_row in conflicts.items():
            out_writer.writerow(out_row)



 """