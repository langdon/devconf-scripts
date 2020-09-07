from collections import OrderedDict
from copy import deepcopy
from enum import Enum
from datetime import datetime
import csv
import munch

"""
Next change should be to refactor this all as inheritance :/
"""

_track_lookup = {
    "AD&C": "Application Development & Containerization",
    "B&RCI": "Building and Running Cloud Infra",
    "ESQ": "Ensuring Software Quality",
    "ET": "Evolving Technology",
    #    "ML": "ML: Privacy & Big Data",
    "ML&AI": "ML & AI",
    "OSP": "Open Source & Process",
    "OSc": "Operating at Scale",
    "S": "Serverless",
    "SPDG": "Security, Privacy, & Data Governance",
    "SE&H": "Systems Engineering & Hardware",
    "UX": "User Experience in OS"}


class Talk_Types(Enum):
    CAN = 0
    SCHED_TYPE = 1
    CONFIRMED = 2
    ACCEPTED = 3
    PLANNING = 4
    CFP = 5


VIRTUAL = True


class Sched_Talk():
    field_names = ["ID", "Title", "Published?", "Start Date & Time", "End Date & Time", "Type/Track", "Sub-type",
                   "Capacity", "Description", "Speakers", "Moderators", "Artists", "Sponsors", "Exhibitors", "Venue",
                   "Physical Address", "Link To Image File", "Tags", "Custom Filter 1", "Custom Filter 2", "Custom Filter 3",
                   "Custom Filter 4", "Host Organization", "Feedback Survey URL", "Collect y/n", "Track"]

    sched_template = OrderedDict([
        ('ID', ''),
        ('Title', ''),
        ('Published?', ''),
        ('Pinned?', ''),
        ('Start Date & Time', ''),
        ('End Date & Time', ''),
        ('Type/Track', ''),
        ('Sub-type', ''),
        ('Capacity', ''),
        ('Description', ''),
        ('Speakers', ''),
        ('Moderators', ''),
        ('Artists', ''),
        ('Sponsors', ''),
        ('Exhibitors', ''),
        ('Venue', ''),
        ('Physical Address', ''),
        ('Link To Image File', ''),
        ('Tags', ''),
        ('Custom Filter 1', ''),
        ('Custom Filter 2', ''),
        ('Custom Filter 3', ''),
        ('Custom Filter 4', ''),
        ('Host Organization', ''),
        ('Feedback Survey URL', ''),
        ('Collect y/n', ''),
        ('Track', '')])

    @staticmethod
    def to_sched(can_talk):
        #talk = deepcopy(Sched_Talk.sched_template)
        talk = {}
        talk['ID'] = can_talk.id
        talk['Title'] = can_talk.title
        talk['Published?'] = 'Y' if can_talk.published else 'N'
        talk['Start Date & Time'] = can_talk.start
        talk['End Date & Time'] = can_talk.end
        talk['Type/Track'] = can_talk.track
        talk['Description'] = can_talk.abstract
        talk['Speakers'] = can_talk.speakers
        talk['Venue'] = can_talk.venue
        talk['Physical Address'] = can_talk.address
        talk['Collect y/n'] = 'Y' if can_talk.feedback_y else 'N'
        return talk

    @staticmethod
    def to_canonical(messy_talk):
        talk = Canonical_Talk()
        #talk = deepcopy(talk_template)
        talk['source'] = Talk_Types.SCHED_TYPE
        talk['id'] = messy_talk['ID']
        talk['title'] = messy_talk['Title']
        talk['published'] = True if messy_talk['Published?'] == 'Y' else False
        talk['start'] = messy_talk['Start Date & Time']
        talk['start'] = datetime.strptime(
            talk.start, '%m/%d/%Y %H:%M') if talk.start is not None and talk.start is not '' else None
        talk['end'] = messy_talk['End Date & Time']
        talk['end'] = datetime.strptime(
            talk.end, '%m/%d/%Y %H:%M') if talk.end is not None and talk.end is not '' else None
        talk['track'] = messy_talk['Type/Track']
        talk['abstract'] = messy_talk['Description']
        talk['speakers'] = messy_talk['Speakers']
        talk['venue'] = messy_talk['Venue']
        talk['address'] = messy_talk['Physical Address']
        talk['feedback_y'] = True if messy_talk['Collect y/n'] == 'Y' else False
        return talk

    @staticmethod
    def write_output(talks_in, output_fn, **kwargs):
        with open(output_fn, 'w') as csvfile:
            out_writer = csv.DictWriter(
                csvfile, fieldnames=Sched_Talk.field_names, quoting=csv.QUOTE_ALL, **kwargs)
            out_writer.writeheader()
            talks = talks_in.items() if "items" in dir(talks_in) else talks_in
            for talk in talks:
                talk = Sched_Talk.to_sched(talk)
                out_writer.writerow(talk)


class Confirmed_Talk():
    field_names = ["ID", "Track", "Order", "Title",
                   "Speaker", "Confirmed", "Constraints", "Abstract"]
#    field_names = ["ID", "Track ID", "Type/Track", "Order", "Title", "Speakers", "Confirmed", "Constraints", "Abstract"]

    confirmed_template = OrderedDict([
        ('ID', ''),
        ('Track', ''),
        ('Order', ''),
        ('Title', ''),
        ('Speakers', ''),
        ('Confirmed', ''),
        ('Constraints', ''),
        ('Abstract', '')])

    @staticmethod
    def to_confirmed(can_talk):
        talk = deepcopy(Confirmed_Talk.confirmed_template)
        talk['ID'] = can_talk.id
        talk['Track'] = can_talk.track
        talk['Order'] = can_talk.order if "Order" in can_talk else -1
        talk['Title'] = can_talk.title
        talk['Speakers'] = can_talk.speakers
        if "confirmed" in can_talk:
            if can_talk.confirmed == True:
                talk['Confirmed'] = 'Yes'
            elif can_talk.confirmed == False:
                talk['Confirmed'] = 'No'
            else:
                talk['Confirmed'] = "Unknown"
        talk['Abstract'] = can_talk.abstract
        return talk

    @staticmethod
    def to_canonical(messy_talk):
        talk = Canonical_Talk()
        #talk = deepcopy(talk_template)
        talk['source'] = Talk_Types.CONFIRMED
        talk['id'] = messy_talk['ID']
        if "Track ID" in messy_talk.keys():
            talk['track'] = _track_lookup[messy_talk['Track ID']]
        elif len(messy_talk['Track']) < 6:
            talk['track'] = _track_lookup[messy_talk['Track']]
        else:
            talk['track'] = messy_talk['Track']
        talk['order'] = messy_talk['Order']
        talk['title'] = messy_talk['Title']
        talk['speakers'] = messy_talk['Speakers']
        talk['confirmed'] = convert_to_boolean(messy_talk['Confirmed'])
        talk['abstract'] = messy_talk['Abstract']
        return talk

    @staticmethod
    def write_output(talks, output_fn, **kwargs):
        with open(output_fn, 'w') as csvfile:
            out_writer = csv.DictWriter(
                csvfile, fieldnames=Confirmed_Talk.field_names, quoting=csv.QUOTE_ALL, **kwargs)
            out_writer.writeheader()
            for talk in talks.values():
                talk = Confirmed_Talk.to_confirmed(talk)
                out_writer.writerow(talk)


class Accepted_Talk():
    field_names = ["ID", "Title", "Type/Track", "Description", "Speakers"]

    @staticmethod
    def to_accepted(can_talk):
        raise NotImplementedError
        # talk = deepcopy(Accepted_Talk.sched_template)
        # talk['ID']                =  can_talk.id
        # talk['Title']             =  can_talk.title
        # talk['Published?']        = 'Y' if can_talk.published else 'N'
        # talk['Start Date & Time'] =  can_talk.start
        # talk['End Date & Time']   =  can_talk.end
        # talk['Type/Track']        =  can_talk.track
        # talk['Description']       =  can_talk.abstract
        # talk['Speakers']          =  can_talk.speakers
        # talk['Venue']             =  can_talk.venue
        # talk['Physical Address']  =  can_talk.address
        # talk['Collect y/n']       = 'Y' if can_talk.feedback_y else 'N'
        # return talk

    @staticmethod
    def to_canonical(messy_talk):
        talk = Canonical_Talk()
        #talk = deepcopy(talk_template)
        talk['source'] = Talk_Types.ACCEPTED
        talk['id'] = messy_talk['ID']
        talk['track'] = messy_talk['Type/Track']
        talk['title'] = messy_talk['Title']
        talk['speakers'] = messy_talk['Speakers']
        talk['abstract'] = messy_talk['Description']
        return talk

    @staticmethod
    def write_output(talks, output_fn, **kwargs):
        with open(output_fn, 'w') as csvfile:
            out_writer = csv.DictWriter(
                csvfile, fieldnames=Accepted_Talk.field_names, quoting=csv.QUOTE_ALL, **kwargs)
            out_writer.writeheader()
            for talk in talks.items():
                talk = Accepted_Talk.to_accepted(talk)
                out_writer.writerow(talk)


class Planning_Talk():
    field_names = ["ID", "Type/Track", "Title", "Speakers", "Votes", "Confirmed",
                   "Accepted", "Axe Talk", "Waitlist", "BWMAM", "Workshop", "Constraints", "Order"]

    @staticmethod
    def to_accepted(can_talk):
        raise NotImplementedError

    @staticmethod
    def to_canonical(messy_talk, talks):
        talk = Canonical_Talk()
        #talk = deepcopy(talk_template)
        if "ID" in messy_talk.keys() and messy_talk['ID'] is not None and messy_talk['ID'] is not "":
            talk['source'] = Talk_Types.ACCEPTED
            talk['id'] = messy_talk['ID']
            if "Track ID" in messy_talk.keys():
                talk['track'] = _track_lookup[messy_talk['Track ID']]
            elif len(messy_talk['Track']) < 6:
                talk['track'] = _track_lookup[messy_talk['Track']]
            else:
                talk['track'] = messy_talk['Track']
            talk['title'] = messy_talk['Title']
            talk['speakers'] = messy_talk['Speakers']
            talk['votes'] = messy_talk['Votes']
            talk['confirmed'] = convert_to_boolean(messy_talk['Confirmed'])
            talk['accepted'] = convert_to_boolean(messy_talk['Accepted'])
            talk['axed'] = convert_to_boolean(messy_talk['Axe Talk'])
            talk['waitlist'] = convert_to_boolean(messy_talk['Waitlist'])
            talk['bwmam'] = convert_to_boolean(messy_talk['BWMAM'])
            talk['workshop'] = convert_to_boolean(messy_talk['Workshop'])
            talk['constraints'] = messy_talk['Constraints']
            talk['order'] = messy_talk['Order']
            talk['start'] = messy_talk['Start Time'] if (
                "Start Time" in messy_talk.keys()) else None
            talk['end'] = messy_talk['End Time'] if (
                "End Time" in messy_talk.keys()) else None
            talk['venue'] = messy_talk['Venue'] if (
                "Venue" in messy_talk.keys()) else None
            # default to true in *most* cases
            talk['feedback_y'] = False if 'Collect y/n' in messy_talk.keys(
            ) and messy_talk['Collect y/n'] == 'N' else True
            talk['address'] = "Virtual" if VIRTUAL else messy_talk['Address']
        else:
            talk = None
        # axed talks are often duplicated, if we don't do this, it may overwrite the good one
        if talk and talk.id in talks.keys():
            if talk.axed:
                talk = None
        return talk

    @staticmethod
    def write_output(talks, output_fn, **kwargs):
        with open(output_fn, 'w') as csvfile:
            out_writer = csv.DictWriter(
                csvfile, fieldnames=Accepted_Talk.field_names, quoting=csv.QUOTE_ALL, **kwargs)
            out_writer.writeheader()
            for talk in talks.items():
                talk = Accepted_Talk.to_accepted(talk)
                out_writer.writerow(talk)


class CFP_Talk():
    field_names = ["id", "title", "type", "duration", "difficulty", "summary ",
                   "notes", "notes2", "notes3", "keywords", "speakers", "topic",
                   "Video link", "Presentation link"]

    @staticmethod
    def to_accepted(can_talk):
        raise NotImplementedError

    @staticmethod
    def to_canonical(messy_talk):
        talk = Canonical_Talk()
        if "ID" in messy_talk.keys():
            talk['source'] = Talk_Types.CFP
            talk['id'] = messy_talk['ID']
            talk['title'] = messy_talk['title']
            talk['type'] = messy_talk['type']
            talk['duration'] = messy_talk['duration']
            talk['difficulty'] = messy_talk['difficulty']
            talk['abstract'] = messy_talk['abstract']
            talk['summary'] = messy_talk['summary']
            talk['notes'] = messy_talk['notes']
            talk['notes2'] = messy_talk['notes2']
            talk['notes3'] = messy_talk['notes3']
            talk['keywords'] = messy_talk['keywords']
            talk['speakers'] = messy_talk['speakers']
            talk['topic'] = messy_talk['topic']
            talk['v_link'] = messy_talk['Video link']
            talk['p_link'] = messy_talk['Presentation link']
        else:
            talk = None
        return talk

    @staticmethod
    def write_output(talks, output_fn, **kwargs):
        with open(output_fn, 'w') as csvfile:
            out_writer = csv.DictWriter(
                csvfile, fieldnames=Accepted_Talk.field_names, quoting=csv.QUOTE_ALL, **kwargs)
            out_writer.writeheader()
            for talk in talks.items():
                talk = Accepted_Talk.to_accepted(talk)
                out_writer.writerow(talk)

# id	title	type	duration	difficulty	abstract	summary	notes	notes2	notes3	keywords	speakers	topic	Video link	Presentation link


class Canonical_Talk(munch.Munch):
    @staticmethod
    def to_canonical_talk(messy_talk, talks):
        if "Tags" in messy_talk.keys():  # from sched
            return Sched_Talk.to_canonical(messy_talk)
        elif "Axe Talk" in messy_talk.keys():  # litte messy cause also in sched
            return Planning_Talk.to_canonical(messy_talk, talks)
        elif "Video link" in messy_talk.keys():  # litte messy cause also in sched
            return CFP_Talk.to_canonical(messy_talk)
        elif "Confirmed" in messy_talk.keys():
            return Confirmed_Talk.to_canonical(messy_talk)
        elif "Type/Track" in messy_talk.keys():  # litte messy cause also in sched
            return Accepted_Talk.to_canonical(messy_talk)
        raise RuntimeError("Could not find the type of talk this was")

    @staticmethod
    def load_canonical_talks(fn, **kwargs):
        talks = {}
        with open(fn) as csvfile:
            reader = csv.DictReader(csvfile, **kwargs)
            tmp = list(reader)
            for talk in tmp:
                can_talk = Canonical_Talk.to_canonical_talk(talk, talks)
                if can_talk is not None:
                    talks[talk["ID"]] = can_talk
        return talks


def convert_to_boolean(value):
    if value == '' or value is None:
        return None
    elif value == "Yes":
        return True
    elif value.lower() == "true":
        return True
    else:
        return False


def get_talk(talks, value, label="ID"):
    loc_talks = talks
    if isinstance(talks, dict):
        loc_talks = [v for v in talks.values()]
    return next(item for item in loc_talks if item[label] == str(value))


talk_template = OrderedDict([
    ('source', ''),
    ('id', ''),
    ('title', ''),
    ('published', ''),
    ('order', ''),
    ('start', ''),
    ('end', ''),
    ('track', ''),
    ('astract', ''),
    ('speakers', ''),
    ('venue', ''),
    ('address', ''),
    ('feedback_y', ''),
    ('confirmed', ''),
    ('track', '')])


"""
    def __init__(self,
        source = '',
        id = '',
        title = '',
        published = '',
        order = '',
        start = '',
        end = '',
        track = '',
        astract = '',
        speakers = '',
        venue = '',
        address = '',
        feedback_y = '',
        confirmed = ''):
        pass
    def __setitem__(self, key, value):
        setattr(self,  key, value)
"""
