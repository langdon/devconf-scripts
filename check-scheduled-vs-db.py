import csv
import pprint
from datetime import datetime

db_titles = {}
sched_talks = {}
pp = pprint.PrettyPrinter(indent=4)
conflicts = {}

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

""" 
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
 """
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



