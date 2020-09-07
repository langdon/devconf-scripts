from collections import OrderedDict
from copy import deepcopy
from enum import Enum
from autoclass import autoclass, autodict
import csv
import munch

def clean_up_red_hat(org):
    if org:
        correct = "Red Hat, Inc."
        test = str(org).lower()
        if "redhat" in test:
            org = correct
        elif "red hat" in test:
            org = correct
    return org

class Canonical_Speaker(munch.Munch):
    @staticmethod
    def to_canonical_speaker(messy_speaker):
        if 'Timestamp' in messy_speaker.keys():
            return CFP_Speaker.to_canonical_speaker(messy_speaker)
        elif "Password" in messy_speaker.keys():
            return Sched_Speaker.to_canonical_speaker(messy_speaker)
        elif "Avatar" in messy_speaker.keys():
            return CFP_App_Speaker.to_canonical_speaker(messy_speaker)

    @staticmethod
    def load_canonical_speakers(fn, **kwargs):
        speakers = {}
        with open(fn) as csvfile:
            reader = csv.DictReader(csvfile, **kwargs)
            tmp = list(reader)
            for speaker in tmp:
                speaker = Canonical_Speaker.to_canonical_speaker(speaker)
                speakers[speaker.email] = speaker
        return speakers

class Sched_Speaker():
    field_names = ["Name (Required)", "Email Address", "Password", "Company", "Position", "Location",
                    "Bio/Description", "Website URL", "Link To Image File", "Tags"]

    @staticmethod
    def to_canonical_speaker(messy_speaker):
        speaker = Canonical_Speaker()
        speaker.name = messy_speaker["Name (Required)"]
        speaker.email = messy_speaker["Email Address"]
        speaker.password = messy_speaker["Password"]
        speaker.company = messy_speaker["Company"]
        speaker.position = messy_speaker["Position"]
        speaker.location = messy_speaker["Location"]
        speaker.bio = messy_speaker["Bio/Description"]
        speaker.url = messy_speaker["Website URL"]
        speaker.image_url = messy_speaker["Link To Image File"]
        speaker.tags = messy_speaker["Tags"]
        return speaker

    @staticmethod
    def to_sched_speaker(can_speaker):
        sched_speaker = OrderedDict()
        sched_speaker["Name (Required)"] = can_speaker.name if 'name' in can_speaker else None
        sched_speaker["Email Address"] = can_speaker.email if 'email' in can_speaker else None
        sched_speaker["Password"] = can_speaker.password if 'password' in can_speaker else None
        sched_speaker["Company"] = clean_up_red_hat(can_speaker.company if 'company' in can_speaker else None)
        sched_speaker["Position"] = can_speaker.position if 'position' in can_speaker else None
        sched_speaker["Location"] = can_speaker.location if 'location' in can_speaker else None
        sched_speaker["Bio/Description"] = can_speaker.bio if 'bio' in can_speaker else None
        sched_speaker["Website URL"] = can_speaker.url if 'url' in can_speaker else None
        sched_speaker["Link To Image File"] = can_speaker.image_url if 'image_url' in can_speaker else None
        sched_speaker["Tags"] = can_speaker.tags if 'tags' in can_speaker else None
        return sched_speaker

    @staticmethod
    def write_output(speakers, output_fn, **kwargs):
        sched_speakers = []
        for email, speaker in speakers.items():
            sched_speakers.append(Sched_Speaker.to_sched_speaker(speaker))
        with open(output_fn, 'w') as csvfile:
            out_writer = csv.DictWriter(csvfile, fieldnames=Sched_Speaker.field_names, quoting=csv.QUOTE_ALL, **kwargs)
            out_writer.writeheader()
            out_writer.writerows(sched_speakers)

class CFP_Speaker():
    field_name = ["Timestamp", "Email Address", "Submission Type", "Volunteer - I am willing to...",
            "Volunteer - Anything else you'd like to mention?", "Booth Title", "Booth Description", "Booth Reservation Dates",
            "Booth Requirements", "BoF Title", "BoF Description", "BoF Date", "BoF Duration", "BoF Capacity",
            "BoF projector / screen is required?", "BoF private room is required?", "BoF requirements", "Session Title",
            "Session Type", "Session Duration", "Session Themes", "Session Difficulty", "Session Abstract", "Session Summary",
            "Session Notes", "Primary Profile Name", "Primary Profile Picture", "Primary Profile Short Description",
            "Primary Profile Biography", "Primary Profile Organization", "Primary Profile Community",
            "Primary Profile Wearable Size Preference", "Primary Profile Wearable Size Gender Preference",
            "Primary Profile Twitter URL", "Primary Profile GitHub URL", "Primary Profile Website URL",
            "Is there another profile to add?", "Second Profile Name", "Second Profile Email", "Second Profile Picture",
            "Second Profile Short Description", "Second Profile Biography", "Second Profile Organization", "Secondary Profile Community",
            "Second Profile Wearable Size Preference", "Second Profile Wearable Size Gender Preference",
            "Second Profile Twitter URL", "Second Profile GitHub URL", "Second Profile Website URL",
            "Is there another profile to add?", "Third Profile Name", "Third Profile Email", "Third Profile Picture",
            "Third Profile Short Description", "Third Profile Biography", "Third Profile Organization", "Third Profile Community",
            "Third Profile Wearable Size Preference", "Third Profile Wearable Size Gender Preference", "Third Profile Twitter URL",
            "Third Profile GitHub URL", "Third Profile Website URL",
            "I and all other secondary participants have read, and agree with the DevConf participation agreement"]

    @staticmethod
    def _get_speaker_url(speaker, prefix = ""):
        url = speaker[prefix + "Website URL"].strip()
        if not url:
            url = speaker[prefix + "GitHub URL"].strip()
            if not url:
                url = speaker[prefix + "Twitter URL"].strip()
        return url

    @staticmethod
    def _get_speaker(speaker, messy_speaker, prefix = "Primary Profile "):
        speaker.name = messy_speaker[prefix + "Name"]
        speaker.company = clean_up_red_hat(messy_speaker[prefix + "Organization"])
        speaker.position = messy_speaker[prefix + "Short Description"]
        speaker.bio = messy_speaker[prefix + "Biography"]
        speaker.url = CFP_Speaker._get_speaker_url(messy_speaker, prefix)
        speaker.image_url = messy_speaker[prefix + "Picture"]
        speaker.wearable_gender = messy_speaker[prefix + "Wearable Size Gender Preference"]
        speaker.wearable_size = messy_speaker[prefix + "Wearable Size Preference"]

    @staticmethod
    def to_canonical_speaker(messy_speaker):
        """may return as many as 3 different speakers
        """

        speakers = {}
        #get primary
        speaker = Canonical_Speaker()
        CFP_Speaker._get_speaker(speaker, messy_speaker)
        speaker.email = messy_speaker["Email Address"]
        if speaker.name.strip() and speaker.email.strip():
            speakers[speaker.email] = speaker

        #get second
        speaker = Canonical_Speaker()
        CFP_Speaker._get_speaker(speaker, messy_speaker, "Second Profile ")
        speaker.email = messy_speaker["Second Profile Email"]
        if speaker.name.strip() and speaker.email.strip():
            speakers[speaker.email] = speaker

        #get third
        speaker = Canonical_Speaker()
        CFP_Speaker._get_speaker(speaker, messy_speaker, "Third Profile ")
        speaker.email = messy_speaker["Third Profile Email"]
        if speaker.name.strip() and speaker.email.strip():
            speakers[speaker.email] = speaker

        return speakers

class CFP_App_Speaker():
    field_name = ["Email", "Full Name", "Bio", "Organization", "Position", "Country", "Avatar"]

    @staticmethod
    def to_canonical_speaker(messy_speaker):
        speaker = Canonical_Speaker()
        speaker.name = messy_speaker["Full Name"]
        speaker.company = clean_up_red_hat(messy_speaker["Organization"])
        speaker.position = messy_speaker["Position"]
        speaker.bio = messy_speaker["Bio"]
        speaker.image_url = messy_speaker["Avatar"]
        speaker.email = messy_speaker["Email"]
        speaker.country = messy_speaker["Country"]

        return speaker

