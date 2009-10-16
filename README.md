Twitter backup
==============

`TwitterBackup.py` is a simple script to create a full archive of a user's unique Twitter activity:

- Tweets
- Sent Direct Messages (DMs)
- Received DMs

It (currently) fetches a full archive on every run, and prints the result to `stdout` as JSON of the structure:
    
    {
        'tweets' : [...],
        'direct_messages' : {
            'sent' : [...],
            'received' : [...]
        }
    }

The project also provides a wrapper shell script, `twitter-backup`, to easily pipe this json to a file of the name `archive-<date>.json`.

TwitterBackup (currently) fetches the password for the account from the Mac OS X keychain, by looking for an "internet password" entity with a host containing "twitter.com" and an account name matching the given username. Such entries are automatically added to your keychain when you save your password for the given account in Safari (among other applications). (It specifically dispatches the command `security find-internet-password -s twitter.com -a <username> -g` to fetch the password—try running this command by-hand to see what it should be finding.)

There is also a sample launchd plist describing a launch agent which will automatically invoke the backup every 72 hours, but this has not been significantly tested.


Usage
-----
Given an appropriate entry in the keychain for `<username>`, running:

    % twitter-backup <username> [<path-to-archive>]

will produce:

    <path-to-archive>/archive-<year>-<month>-<day>-<hour>:<minute>:<second>.json


Requirements
------------

TwitterBackup relies on two key external libraries:

- [`simplejson`](http://undefined.org/python/#simplejson)
- ["Python Twitter Tools,"](http://mike.verdone.ca/twitter/) aka `twitter`

To fetch them, if you don't already have them, it is easiest to:

    % easy_install simplejson
    % easy_install twitter

