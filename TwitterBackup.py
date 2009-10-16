import sys
import subprocess
import twitter
import simplejson
import time

usage = """
Usage:
    TwitterBackup <username>
"""

def GetTwitterPassword( account ):
    """Fetch the Twitter password securely from the Keychain"""
    # TODO: add error handling, user involvement
    keychainCmd = 'security find-internet-password' \
                + ' -s twitter.com -a %s -g' \
                % account
    subproc = subprocess.Popen( keychainCmd,
                                shell = True,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE,
                                close_fds = True )
    try:
        passwd = subproc.stderr.read( )
        passwd = passwd.split( '"' )
        assert passwd[ 0 ] == 'password: '
        passwd = passwd[ 1 ]
        assert passwd
    except:
        raise Exception('Failed to find password for %s in default keychain(s)' % account)
    return passwd

# TODO: add retry decorators


# TODO: rewrite to load from disk, begin with since_id from last-stored, and merge back to disk
# For now, we just always suck all messages and re-save them, with the current date.
def FetchAllBeforeID( fetch, fromId, maxTries = 5 ):
    print >> sys.stderr, 'FetchAllFromID',fromId
    fetched = fetch( fromId )
    if fetched:
        print >> sys.stderr, len( fetched )
        maxId = min( [ msg[ 'id' ] for msg in fetched ] )
        # TODO: clean up retry with @decorator, a la http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
        rest = [ ]
        curTry = 0
        while curTry < maxTries:
            try:
                rest = FetchAllBeforeID( fetch, maxId-1 )
                break
            except:
                print >> sys.stderr, 'API Error. Retrying...'
                time.sleep(1)
        fetched.extend( rest )
    return fetched

class TwitterArchiver(object):
    
    def __init__(self, username, password, max_count=200):
        super(TwitterArchiver, self).__init__()
        api = twitter.Twitter(username, password)
        
        self.fetchReceivedDMsBefore = lambda _id: \
            api.direct_messages( max_id = _id, count = max_count )
        
        self.fetchSentDMsBefore = lambda _id: \
            api.direct_messages.sent( max_id = _id, count = max_count )
        
        self.fetchTweetsBefore = lambda _id: \
            api.statuses.user_timeline( max_id = _id, count = max_count )
    
    def fetchTweets(self):
        return FetchAllBeforeID(self.fetchTweetsBefore, sys.maxint)
    
    def fetchReceivedDMs(self):
        return FetchAllBeforeID(self.fetchReceivedDMsBefore, sys.maxint)
    
    def fetchSentDMs(self):
        return FetchAllBeforeID(self.fetchSentDMsBefore, sys.maxint)
    


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            print >> sys.stderr, 'ERROR: improper arguments'
            raise Exception()
        
        username = sys.argv[1]
        
        if username == '-h' or username == '--help':
            raise Exception()
    except:
        print >> sys.stderr, usage
        sys.exit(1)
    
    archiver = TwitterArchiver(username, GetTwitterPassword(username))
    
