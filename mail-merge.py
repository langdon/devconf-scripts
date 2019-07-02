import csv
import pprint
import re
from datetime import datetime
import urllib.parse
import requests
import argparse
import os.path

_message_separator="\n--------------------------------------------------------------\n"
pp = pprint.PrettyPrinter(indent=4)

def send_mail(recipient, subject, message):
    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(_sandbox)
    if (_bcc_addy):
        request = requests.post(request_url, auth=('api', _key), data={
            'from': _from_addy,
            'to': recipient,
            'bcc': _bcc_addy,
            'subject': subject,
            'text': message
        })
    else:
        request = requests.post(request_url, auth=('api', _key), data={
            'from': _from_addy,
            'to': recipient,
            'subject': subject,
            'text': message
        })
    print ('Status: {0}'.format(request.status_code))
    print ('Body:   {0}'.format(request.text))

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--send", action="store_true", dest="send_email", 
	help="actually send emails")
ap.add_argument("-d", "--debug", action="store_true", dest="debug_email", 
	help="send emails to debug address")
ap.add_argument("-a", "--addressees", required=True, dest="addressees_fn", 
	help="csv file with recipient information. Anything with <column-name> will be replaced " +
        "by element from that column. Case matters on column name. Email address must be " + 
        "in a column called 'email'")
ap.add_argument("-t", "--template", required=True, dest="template_fn", 
	help="Email template file. Should have <column-name> where info should be replaced. Case matters.")
ap.add_argument("--subject", dest="subject", 
	help="Subject should be the first line of the template with the keyword 'Subject: ' " + 
        "or may be passed here")
args = vars(ap.parse_args())

_debug_email = args["debug_email"]
_send_email = args["send_email"]

pp.pprint(args)

if _send_email: print("Actually planning to send emails")
else: print("Only writing to file (no email will be sent)")
if _debug_email: print("Sending debug emails")
else: print("sending normal, not debug, emails")

_email_column_name = "email"
_encode_flag = "-encode"
_key = 'key-938992c358af3648e3c12bd00b97bb5d'
_sandbox = 'devconf.us'
_from_addy = 'info@devconf.us'
if _debug_email: 
    _bcc_addy = 'langdon@redhat.com'
else:
    #_bcc_addy = 'info@devconf.us'
    _bcc_addy = ''

addressees_fn = args["addressees_fn"]
if not os.path.isfile(addressees_fn):
    print("{0} does not exist.".format(addressees_fn))
    exit()
template_fn = args["template_fn"]
if not os.path.isfile(template_fn):
    print("{0} does not exist.".format(template_fn))
    exit()

template = ""
with open(template_fn) as template_file:
    template = template_file.read()
    _subject = args["subject"] 
    if (_subject is None or _subject == ""):
        if (re.match('Subject:\s*(.*)', template) is not None):
            _subject = re.match('Subject:\s*(.*)', template).group(1)
            template = re.sub('Subject:.*\n','', template)
        else: 
            print("You didn't provide an email subject. Use --subject or put it in the template with 'Subject: ' at the beginning")
            exit()

    print("Subject: '" + _subject + "'")
    print("template: \n" + template)

print("Using from_addy: {0}, bcc_addy: {1}, _subject: {2}".format(_from_addy, _bcc_addy, _subject) )

addressees = []

with open(addressees_fn) as csvfile:
    addressee_reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    
    #get fieldnames from DictReader object and store in list
    if _email_column_name not in addressee_reader.fieldnames:
        print("you must provide email addresses in a column called 'email' & case matters. RFE: make this a cli param")
        exit()

    replacements = {}
    for column_name in addressee_reader.fieldnames:
        replacements[column_name] = "<" + column_name + ">"

    with open('messages.txt', 'w') as messages_file:
        message = ""
        for row in addressee_reader:
            message = template 
            for replacement, search in replacements.items():
                #check if the content has to be specially treated
                if _encode_flag in search:
                    r = urllib.parse.quote_plus(row[replacement])
                else:
                    r = row[replacement]
                message = message.replace(search, r) 
            messages_file.write(message)
            messages_file.write(_message_separator)
            if _send_email:
                if _debug_email:
                    print('Sending {0} to {1}: '.format(_subject, 'lwhite+debug@fishjump.com'))
                    send_mail('lwhite+debug@fishjump.com', _subject, message)
                else:
                    print('Sending {0} to {1}: '.format(_subject, row[_email_column_name]))
                    send_mail(row[_email_column_name], _subject, message)
