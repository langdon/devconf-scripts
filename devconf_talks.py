from collections import OrderedDict
from copy import deepcopy
from enum import Enum
import csv
import munch

"""
Next change should be to refactor this all as inheritance :/
"""

_track_lookup = {
    "AD&C": "Application Development & Containerization",
    "B&RCI": "Building and Running Cloud Infra",
    "ESQ": "Ensuring Software Quality",
    "ML": "ML: Privacy & Big Data",
    "OSP": "Open Source & Process",
    "S": "Serverless",
    "SE&H": "Systems Engineering & Hardware",
    "UX": "User Experience in OS"}

class Talk_Types(Enum):
    CAN = 0
    SCHED_TYPE = 1
    CONFIRMED = 2
    ACCEPTED = 3

class Sched_Talk():
    field_names = ["ID", "Title", "Published?", "Start Date & Time", "End Date & Time", "Type/Track", "Sub-type", 
                    "Capacity", "Description", "Speakers", "Moderators", "Artists", "Sponsors", "Exhibitors", "Venue", 
                    "Physical Address", "Link To Image File", "Tags", "Custom Filter 1", "Custom Filter 2", "Custom Filter 3",
                    "Custom Filter 4", "Host Organization", "Feedback Survey URL", "Collect y/n", "Track"]

    sched_template = OrderedDict([
        ('ID', ''), 
        ('Title', ''), 
        ('Published?', ''), 
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
        talk = deepcopy(Sched_Talk.sched_template)
        talk['ID']                =  can_talk.id
        talk['Title']             =  can_talk.title
        talk['Published?']        = 'Y' if can_talk.published else 'N'
        talk['Start Date & Time'] =  can_talk.start
        talk['End Date & Time']   =  can_talk.end
        talk['Type/Track']        =  can_talk.track
        talk['Description']       =  can_talk.abstract
        talk['Speakers']          =  can_talk.speakers
        talk['Venue']             =  can_talk.venue
        talk['Physical Address']  =  can_talk.address
        talk['Collect y/n']       = 'Y' if can_talk.feedback_y else 'N'
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
        talk['end'] = messy_talk['End Date & Time']
        talk['track'] = messy_talk['Type/Track']
        talk['abstract'] = messy_talk['Description']
        talk['speakers'] = messy_talk['Speakers']
        talk['venue'] = messy_talk['Venue']
        talk['address'] = messy_talk['Physical Address']
        talk['feedback_y'] = True if messy_talk['Collect y/n'] == 'Y' else False
        return talk

    @staticmethod
    def write_output(talks, output_fn, **kwargs):
        with open(output_fn, 'w') as csvfile:
            out_writer = csv.DictWriter(csvfile, fieldnames=Sched_Talk.field_names, quoting=csv.QUOTE_ALL, **kwargs)
            out_writer.writeheader()
            for talk in talks.items():
                talk = Sched_Talk.to_sched(talk)
                out_writer.writerow(talk)


class Confirmed_Talk():
    field_names = ["ID", "Track", "Order", "Title", "Speaker", "Confirmed", "Constraints", "Abstract"]
#    field_names = ["ID", "Track ID", "Type/Track", "Order", "Title", "Speaker", "Confirmed", "Constraints", "Abstract"]

    confirmed_template = OrderedDict([
        ('ID', ''),
        ('Track', ''),
        ('Order', ''),
        ('Title', ''),
        ('Speaker', ''),
        ('Confirmed', ''),
        ('Constraints', ''),
        ('Abstract', '')])

    @staticmethod
    def to_confirmed(can_talk):
        talk = deepcopy(Confirmed_Talk.confirmed_template)
        talk['ID']        = can_talk.id
        talk['Track']     = can_talk.track
        talk['Order']     = can_talk.order if "Order" in can_talk else -1
        talk['Title']     = can_talk.title
        talk['Speaker']   = can_talk.speakers
        if "confirmed" in can_talk:
            if can_talk.confirmed == True:
                talk['Confirmed'] = 'Yes'
            elif can_talk.confirmed == False:
                talk['Confirmed'] = 'No'
            else:
                talk['Confirmed'] = "Unknown"
        talk['Abstract']  = can_talk.abstract
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
        talk['speakers'] = messy_talk['Speaker']
        if "Confirmed" in messy_talk:
            if messy_talk['Confirmed'] == 'Yes':
                talk['confirmed'] = True
            elif messy_talk['Confirmed'] == 'No':
                talk['confirmed'] = False
            else:
                talk['confirmed'] = "Unknown"
        talk['abstract'] = messy_talk['Abstract']
        return talk

    @staticmethod
    def write_output(talks, output_fn, **kwargs):
        with open(output_fn, 'w') as csvfile:
            out_writer = csv.DictWriter(csvfile, fieldnames=Confirmed_Talk.field_names, quoting=csv.QUOTE_ALL, **kwargs)
            out_writer.writeheader()
            for talk in talks.values():
                talk = Confirmed_Talk.to_confirmed(talk)
                out_writer.writerow(talk)

class Accepted_Talk():
    field_names = ["ID","Title","Type/Track","Description","Speakers"]

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
            out_writer = csv.DictWriter(csvfile, fieldnames=Accepted_Talk.field_names, quoting=csv.QUOTE_ALL, **kwargs)
            out_writer.writeheader()
            for talk in talks.items():
                talk = Accepted_Talk.to_accepted(talk)
                out_writer.writerow(talk)

class Canonical_Talk(munch.Munch):
    @staticmethod
    def to_canonical_talk(messy_talk):
        if "Tags" in messy_talk.keys(): #from sched
            return Sched_Talk.to_canonical(messy_talk)
        elif "Confirmed" in messy_talk.keys():
            return Confirmed_Talk.to_canonical(messy_talk) 
        elif "Type/Track" in messy_talk.keys(): #litte messy cause also in sched
            return Accepted_Talk.to_canonical(messy_talk) 
        raise RuntimeError("Could not find the type of talk this was")

    @staticmethod
    def load_canonical_talks(fn, **kwargs):
        talks = {}
        with open(fn) as csvfile:
            reader = csv.DictReader(csvfile, **kwargs)
            tmp = list(reader)
            for talk in tmp:
                talks[talk["ID"]] = Canonical_Talk.to_canonical_talk(talk)
        return talks

def get_talk(talks, value, label = "ID"):
    loc_talks = talks
    if isinstance(talks, dict):
        loc_talks = [ v for v in talks.values() ]
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