#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with this library; if not, write to the 
#      Free Software Foundation, Inc., 
#      59 Temple Place, Suite 330, 
#      Boston, MA  02111-1307  USA

# This file is part of urlgrabber, a high-level cross-protocol url-grabber
# Copyright 2002-2004 Michael D. Stenner, Ryan Tomayko
# Copyright 2009 Red Hat inc, pycurl code written by Seth Vidal

"""A high-level cross-protocol url-grabber.

GENERAL ARGUMENTS (kwargs)

  Where possible, the module-level default is indicated, and legal
  values are provided.

  copy_local = 0   [0|1]

    ignored except for file:// urls, in which case it specifies
    whether urlgrab should still make a copy of the file, or simply
    point to the existing copy. The module level default for this
    option is 0.

  close_connection = 0   [0|1]

    tells URLGrabber to close the connection after a file has been
    transferred. This is ignored unless the download happens with the
    http keepalive handler (keepalive=1).  Otherwise, the connection
    is left open for further use. The module level default for this
    option is 0 (keepalive connections will not be closed).

  keepalive = 1   [0|1]

    specifies whether keepalive should be used for HTTP/1.1 servers
    that support it. The module level default for this option is 1
    (keepalive is enabled).

  progress_obj = None

    a class instance that supports the following methods:
      po.start(filename, url, basename, size, now, text)
      # length will be None if unknown
      po.update(read) # read == bytes read so far
      po.end()

  multi_progress_obj = None

    a class instance that supports the following methods:
      mo.start(total_files, total_size)
      mo.newMeter() => meter
      mo.removeMeter(meter)
      mo.end()

   The 'meter' object is similar to progress_obj, but multiple
   instances may be created and updated at the same time.

   When downloading multiple files in parallel and multi_progress_obj
   is None progress_obj is used in compatibility mode: finished files
   are shown but there's no in-progress display.

  text = None
  
    specifies alternative text to be passed to the progress meter
    object.  If not given, the default progress meter will use the
    basename of the file.

  throttle = 1.0

    a number - if it's an int, it's the bytes/second throttle limit.
    If it's a float, it is first multiplied by bandwidth.  If throttle
    == 0, throttling is disabled.  If None, the module-level default
    (which can be set on default_grabber.throttle) is used. See
    BANDWIDTH THROTTLING for more information.

  timeout = 300

    a positive integer expressing the number of seconds to wait before
    timing out attempts to connect to a server. If the value is None
    or 0, connection attempts will not time out. The timeout is passed
    to the underlying pycurl object as its CONNECTTIMEOUT option, see
    the curl documentation on CURLOPT_CONNECTTIMEOUT for more information.
    http://curl.haxx.se/libcurl/c/curl_easy_setopt.html#CURLOPTCONNECTTIMEOUT

  minrate = 1000

    This sets the low speed threshold in bytes per second. If the server
    is sending data slower than this for at least `timeout' seconds, the
    library aborts the connection.

  bandwidth = 0

    the nominal max bandwidth in bytes/second.  If throttle is a float
    and bandwidth == 0, throttling is disabled.  If None, the
    module-level default (which can be set on
    default_grabber.bandwidth) is used. See BANDWIDTH THROTTLING for
    more information.

  range = None

    a tuple of the form (first_byte, last_byte) describing a byte
    range to retrieve. Either or both of the values may set to
    None. If first_byte is None, byte offset 0 is assumed. If
    last_byte is None, the last byte available is assumed. Note that
    the range specification is python-like in that (0,10) will yield
    the first 10 bytes of the file.

    If set to None, no range will be used.
    
  reget = None   [None|'simple'|'check_timestamp']

    whether to attempt to reget a partially-downloaded file.  Reget
    only applies to .urlgrab and (obviously) only if there is a
    partially downloaded file.  Reget has two modes:

      'simple' -- the local file will always be trusted.  If there
        are 100 bytes in the local file, then the download will always
        begin 100 bytes into the requested file.

      'check_timestamp' -- the timestamp of the server file will be
        compared to the timestamp of the local file.  ONLY if the
        local file is newer than or the same age as the server file
        will reget be used.  If the server file is newer, or the
        timestamp is not returned, the entire file will be fetched.

    NOTE: urlgrabber can do very little to verify that the partial
    file on disk is identical to the beginning of the remote file.
    You may want to either employ a custom "checkfunc" or simply avoid
    using reget in situations where corruption is a concern.

  user_agent = 'urlgrabber/VERSION'

    a string, usually of the form 'AGENT/VERSION' that is provided to
    HTTP servers in the User-agent header. The module level default
    for this option is "urlgrabber/VERSION".

  http_headers = None

    a tuple of 2-tuples, each containing a header and value.  These
    will be used for http and https requests only.  For example, you
    can do
      http_headers = (('Pragma', 'no-cache'),)

  ftp_headers = None

    this is just like http_headers, but will be used for ftp requests.

  proxies = None

    a dictionary that maps protocol schemes to proxy hosts. For
    example, to use a proxy server on host "foo" port 3128 for http
    and https URLs:
      proxies={ 'http' : 'http://foo:3128', 'https' : 'http://foo:3128' }
    note that proxy authentication information may be provided using
    normal URL constructs:
      proxies={ 'http' : 'http://user:host@foo:3128' }

  libproxy = False

    Use the libproxy module (if installed) to find proxies.
    The libproxy code is only used if the proxies dictionary
    does not provide any proxies.

  prefix = None

    a url prefix that will be prepended to all requested urls.  For
    example:
      g = URLGrabber(prefix='http://foo.com/mirror/')
      g.urlgrab('some/file.txt')
      ## this will fetch 'http://foo.com/mirror/some/file.txt'
    This option exists primarily to allow identical behavior to
    MirrorGroup (and derived) instances.  Note: a '/' will be inserted
    if necessary, so you cannot specify a prefix that ends with a
    partial file or directory name.

  opener = None
    No-op when using the curl backend (default)

  cache_openers = True
    No-op when using the curl backend (default)

  data = None

    Only relevant for the HTTP family (and ignored for other
    protocols), this allows HTTP POSTs.  When the data kwarg is
    present (and not None), an HTTP request will automatically become
    a POST rather than GET.  This is done by direct passthrough to
    urllib2.  If you use this, you may also want to set the
    'Content-length' and 'Content-type' headers with the http_headers
    option.  Note that python 2.2 handles the case of these
    badly and if you do not use the proper case (shown here), your
    values will be overridden with the defaults.
    
  urlparser = URLParser()

    The URLParser class handles pre-processing of URLs, including
    auth-handling for user/pass encoded in http urls, file handing
    (that is, filenames not sent as a URL), and URL quoting.  If you
    want to override any of this behavior, you can pass in a
    replacement instance.  See also the 'quote' option.

  quote = None

    Whether or not to quote the path portion of a url.
      quote = 1    ->  quote the URLs (they're not quoted yet)
      quote = 0    ->  do not quote them (they're already quoted)
      quote = None ->  guess what to do

    This option only affects proper urls like 'file:///etc/passwd'; it
    does not affect 'raw' filenames like '/etc/passwd'.  The latter
    will always be quoted as they are converted to URLs.  Also, only
    the path part of a url is quoted.  If you need more fine-grained
    control, you should probably subclass URLParser and pass it in via
    the 'urlparser' option.

  username = None
    username to use for simple http auth - is automatically quoted for special characters

  password = None
    password to use for simple http auth - is automatically quoted for special characters

  ssl_ca_cert = None

    this option can be used if M2Crypto is available and will be
    ignored otherwise.  If provided, it will be used to create an SSL
    context.  If both ssl_ca_cert and ssl_context are provided, then
    ssl_context will be ignored and a new context will be created from
    ssl_ca_cert.

  ssl_context = None

    No-op when using the curl backend (default)
   

  ssl_verify_peer = True

    Check the server's certificate to make sure it is valid with what our CA validates
  
  ssl_verify_host = True

    Check the server's hostname to make sure it matches the certificate DN

  ssl_key = None

    Path to the key the client should use to connect/authenticate with

  ssl_key_type = 'PEM'

    PEM or DER - format of key
     
  ssl_cert = None

    Path to the ssl certificate the client should use to to authenticate with

  ssl_cert_type = 'PEM'

    PEM or DER - format of certificate
    
  ssl_key_pass = None

    password to access the ssl_key
    
  size = None

    size (in bytes) or Maximum size of the thing being downloaded. 
    This is mostly to keep us from exploding with an endless datastream
  
  max_header_size = 2097152

    Maximum size (in bytes) of the headers.
    
  ip_resolve = 'whatever'

    What type of name to IP resolving to use, default is to do both IPV4 and
    IPV6.

  async = (key, limit)

    When this option is set, the urlgrab() is not processed immediately
    but queued.  parallel_wait() then processes grabs in parallel, limiting
    the numer of connections in each 'key' group to at most 'limit'.

  max_connections

    The global connection limit.

  timedhosts

    The filename of the host download statistics.  If defined, urlgrabber
    will update the stats at the end of every download.  At the end of
    parallel_wait(), the updated stats are saved.  If synchronous grabs
    are used, you should call th_save().

  default_speed, half_life

    These options only affect the async mirror selection code.
    The default_speed option sets the speed estimate for mirrors
    we have never downloaded from, and defaults to 1 MBps.

    The speed estimate also drifts exponentially from the speed
    actually measured to the default speed, with default
    period of 30 days.

  ftp_disable_epsv = False

    False, True

    This options disables Extended Passive Mode (the EPSV command)
    which does not work correctly on some buggy ftp servers.


RETRY RELATED ARGUMENTS

  retry = None

    the number of times to retry the grab before bailing.  If this is
    zero, it will retry forever. This was intentional... really, it
    was :). If this value is not supplied or is supplied but is None
    retrying does not occur.

  retrycodes = [-1,2,4,5,6,7]

    a sequence of errorcodes (values of e.errno) for which it should
    retry. See the doc on URLGrabError for more details on this.  You
    might consider modifying a copy of the default codes rather than
    building yours from scratch so that if the list is extended in the
    future (or one code is split into two) you can still enjoy the
    benefits of the default list.  You can do that with something like
    this:

      retrycodes = urlgrabber.grabber.URLGrabberOptions().retrycodes
      if 12 not in retrycodes:
          retrycodes.append(12)
      
  checkfunc = None

    a function to do additional checks. This defaults to None, which
    means no additional checking.  The function should simply return
    on a successful check.  It should raise URLGrabError on an
    unsuccessful check.  Raising of any other exception will be
    considered immediate failure and no retries will occur.

    If it raises URLGrabError, the error code will determine the retry
    behavior.  Negative error numbers are reserved for use by these
    passed in functions, so you can use many negative numbers for
    different types of failure.  By default, -1 results in a retry,
    but this can be customized with retrycodes.

    If you simply pass in a function, it will be given exactly one
    argument: a CallbackObject instance with the .url attribute
    defined and either .filename (for urlgrab) or .data (for urlread).
    For urlgrab, .filename is the name of the local file.  For
    urlread, .data is the actual string data.  If you need other
    arguments passed to the callback (program state of some sort), you
    can do so like this:

      checkfunc=(function, ('arg1', 2), {'kwarg': 3})

    if the downloaded file has filename /tmp/stuff, then this will
    result in this call (for urlgrab):

      function(obj, 'arg1', 2, kwarg=3)
      # obj.filename = '/tmp/stuff'
      # obj.url = 'http://foo.com/stuff'
      
    NOTE: both the "args" tuple and "kwargs" dict must be present if
    you use this syntax, but either (or both) can be empty.

  failure_callback = None

    The callback that gets called during retries when an attempt to
    fetch a file fails.  The syntax for specifying the callback is
    identical to checkfunc, except for the attributes defined in the
    CallbackObject instance.  The attributes for failure_callback are:

      exception = the raised exception
      url       = the url we're trying to fetch
      tries     = the number of tries so far (including this one)
      retry     = the value of the retry option

    The callback is present primarily to inform the calling program of
    the failure, but if it raises an exception (including the one it's
    passed) that exception will NOT be caught and will therefore cause
    future retries to be aborted.

    The callback is called for EVERY failure, including the last one.
    On the last try, the callback can raise an alternate exception,
    but it cannot (without severe trickiness) prevent the exception
    from being raised.

  failfunc = None

    The callback that gets called when urlgrab request fails.
    If defined, urlgrab() calls it instead of raising URLGrabError.
    Callback syntax is identical to failure_callback.

    Contrary to failure_callback, it's called only once.  It's primary
    purpose is to use urlgrab() without a try/except block.

  interrupt_callback = None

    This callback is called if KeyboardInterrupt is received at any
    point in the transfer.  Basically, this callback can have three
    impacts on the fetch process based on the way it exits:

      1) raise no exception: the current fetch will be aborted, but
         any further retries will still take place

      2) raise a URLGrabError: if you're using a MirrorGroup, then
         this will prompt a failover to the next mirror according to
         the behavior of the MirrorGroup subclass.  It is recommended
         that you raise URLGrabError with code 15, 'user abort'.  If
         you are NOT using a MirrorGroup subclass, then this is the
         same as (3).

      3) raise some other exception (such as KeyboardInterrupt), which
         will not be caught at either the grabber or mirror levels.
         That is, it will be raised up all the way to the caller.

    This callback is very similar to failure_callback.  They are
    passed the same arguments, so you could use the same function for
    both.
      
BANDWIDTH THROTTLING

  urlgrabber supports throttling via two values: throttle and
  bandwidth Between the two, you can either specify and absolute
  throttle threshold or specify a theshold as a fraction of maximum
  available bandwidth.

  throttle is a number - if it's an int, it's the bytes/second
  throttle limit.  If it's a float, it is first multiplied by
  bandwidth.  If throttle == 0, throttling is disabled.  If None, the
  module-level default (which can be set with set_throttle) is used.

  bandwidth is the nominal max bandwidth in bytes/second.  If throttle
  is a float and bandwidth == 0, throttling is disabled.  If None, the
  module-level default (which can be set with set_bandwidth) is used.

  Note that when multiple downloads run simultaneously (multiprocessing
  or the parallel urlgrab() feature is used) the total bandwidth might
  exceed the throttle limit. You may want to also set max_connections=1
  or scale your throttle option down accordingly.

  THROTTLING EXAMPLES:

  Lets say you have a 100 Mbps connection.  This is (about) 10^8 bits
  per second, or 12,500,000 Bytes per second.  You have a number of
  throttling options:

  *) set_bandwidth(12500000); set_throttle(0.5) # throttle is a float

     This will limit urlgrab to use half of your available bandwidth.

  *) set_throttle(6250000) # throttle is an int

     This will also limit urlgrab to use half of your available
     bandwidth, regardless of what bandwidth is set to.

  *) set_throttle(6250000); set_throttle(1.0) # float

     Use half your bandwidth

  *) set_throttle(6250000); set_throttle(2.0) # float

    Use up to 12,500,000 Bytes per second (your nominal max bandwidth)

  *) set_throttle(6250000); set_throttle(0) # throttle = 0

     Disable throttling - this is more efficient than a very large
     throttle setting.

  *) set_throttle(0); set_throttle(1.0) # throttle is float, bandwidth = 0

     Disable throttling - this is the default when the module is loaded.

  SUGGESTED AUTHOR IMPLEMENTATION (THROTTLING)

  While this is flexible, it's not extremely obvious to the user.  I
  suggest you implement a float throttle as a percent to make the
  distinction between absolute and relative throttling very explicit.

  Also, you may want to convert the units to something more convenient
  than bytes/second, such as kbps or kB/s, etc.

"""



import os
import sys
import urlparse
import time
import string
import urllib
import urllib2
from httplib import responses
import mimetools
import thread
import types
import stat
import pycurl
from ftplib import parse150
from StringIO import StringIO
from httplib import HTTPException
import socket, select, fcntl
from byterange import range_tuple_normalize, range_tuple_to_header, RangeError

try:
    import xattr
    if not hasattr(xattr, 'set'):
        xattr = None # This is a "newer" API.
except ImportError:
    xattr = None


########################################################################
#                     MODULE INITIALIZATION
########################################################################
try:
    exec('from ' + (__name__.split('.'))[0] + ' import __version__')
except:
    __version__ = '???'

try:
    # this part isn't going to do much - need to talk to gettext
    from i18n import _
except ImportError, msg:
    def _(st): return st
    
########################################################################
# functions for debugging output.  These functions are here because they
# are also part of the module initialization.
DEBUG = None
def set_logger(DBOBJ):
    """Set the DEBUG object.  This is called by _init_default_logger when
    the environment variable URLGRABBER_DEBUG is set, but can also be
    called by a calling program.  Basically, if the calling program uses
    the logging module and would like to incorporate urlgrabber logging,
    then it can do so this way.  It's probably not necessary as most
    internal logging is only for debugging purposes.

    The passed-in object should be a logging.Logger instance.  It will
    be pushed into the keepalive and byterange modules if they're
    being used.  The mirror module pulls this object in on import, so
    you will need to manually push into it.  In fact, you may find it
    tidier to simply push your logging object (or objects) into each
    of these modules independently.
    """

    global DEBUG
    DEBUG = DBOBJ

def _init_default_logger(logspec=None):
    '''Examines the environment variable URLGRABBER_DEBUG and creates
    a logging object (logging.logger) based on the contents.  It takes
    the form

      URLGRABBER_DEBUG=level,filename
      
    where "level" can be either an integer or a log level from the
    logging module (DEBUG, INFO, etc).  If the integer is zero or
    less, logging will be disabled.  Filename is the filename where
    logs will be sent.  If it is "-", then stdout will be used.  If
    the filename is empty or missing, stderr will be used.  If the
    variable cannot be processed or the logging module cannot be
    imported (python < 2.3) then logging will be disabled.  Here are
    some examples:

      URLGRABBER_DEBUG=1,debug.txt   # log everything to debug.txt
      URLGRABBER_DEBUG=WARNING,-     # log warning and higher to stdout
      URLGRABBER_DEBUG=INFO          # log info and higher to stderr
      
    This function is called during module initialization.  It is not
    intended to be called from outside.  The only reason it is a
    function at all is to keep the module-level namespace tidy and to
    collect the code into a nice block.'''

    try:
        if logspec is None:
            logspec = os.environ['URLGRABBER_DEBUG']
        dbinfo = logspec.split(',')
        import logging
        level = logging._levelNames.get(dbinfo[0], None)
        if level is None: level = int(dbinfo[0])
        if level < 1: raise ValueError()

        formatter = logging.Formatter('%(asctime)s %(message)s')
        if len(dbinfo) > 1: filename = dbinfo[1]
        else: filename = ''
        if filename == '': handler = logging.StreamHandler(sys.stderr)
        elif filename == '-': handler = logging.StreamHandler(sys.stdout)
        else:  handler = logging.FileHandler(filename)
        handler.setFormatter(formatter)
        DBOBJ = logging.getLogger('urlgrabber')
        DBOBJ.propagate = False
        DBOBJ.addHandler(handler)
        DBOBJ.setLevel(level)
    except (KeyError, ImportError, ValueError):
        DBOBJ = None
    set_logger(DBOBJ)

def _log_package_state():
    if not DEBUG: return
    DEBUG.debug('urlgrabber version  = %s' % __version__)
    DEBUG.debug('trans function "_"  = %s' % _)
        
_init_default_logger()
_log_package_state()


# normally this would be from i18n or something like it ...
def _(st):
    return st

########################################################################
#                 END MODULE INITIALIZATION
########################################################################

########################################################################
#                 UTILITY FUNCTIONS
########################################################################

# These functions are meant to be utilities for the urlgrabber library to use.

def _to_utf8(obj, errors='replace'):
    '''convert 'unicode' to an encoded utf-8 byte string '''
    # stolen from yum.i18n
    if isinstance(obj, unicode):
        obj = obj.encode('utf-8', errors)
    return obj

def exception2msg(e):
    try:
        return str(e)
    except UnicodeEncodeError:
        # always use byte strings
        return unicode(e).encode('utf8')

########################################################################
#                 END UTILITY FUNCTIONS
########################################################################


class URLGrabError(IOError):
    """
    URLGrabError error codes:

      URLGrabber error codes (0 -- 255)
        0    - everything looks good (you should never see this)
        1    - malformed url
        2    - local file doesn't exist
        3    - request for non-file local file (dir, etc)
        4    - IOError on fetch
        5    - OSError on fetch
        6    - no content length header when we expected one
        7    - HTTPException
        8    - Exceeded read limit (for urlread)
        9    - Requested byte range not satisfiable.
        10   - Byte range requested, but range support unavailable
        11   - Illegal reget mode
        12   - Socket timeout
        13   - malformed proxy url
        14   - HTTPError (includes .code and .exception attributes)
        15   - user abort
        16   - error writing to local file
        
      MirrorGroup error codes (256 -- 511)
        256  - No more mirrors left to try

      Custom (non-builtin) classes derived from MirrorGroup (512 -- 767)
        [ this range reserved for application-specific error codes ]

      Retry codes (< 0)
        -1   - retry the download, unknown reason

    Note: to test which group a code is in, you can simply do integer
    division by 256: e.errno / 256

    Negative codes are reserved for use by functions passed in to
    retrygrab with checkfunc.  The value -1 is built in as a generic
    retry code and is already included in the retrycodes list.
    Therefore, you can create a custom check function that simply
    returns -1 and the fetch will be re-tried.  For more customized
    retries, you can use other negative number and include them in
    retry-codes.  This is nice for outputting useful messages about
    what failed.

    You can use these error codes like so:
      try: urlgrab(url)
      except URLGrabError, e:
         if e.errno == 3: ...
           # or
         print e.strerror
           # or simply
         print e  #### print '[Errno %i] %s' % (e.errno, e.strerror)
    """
    def __init__(self, *args):
        IOError.__init__(self, *args)
        self.url = "No url specified"

class CallbackObject:
    """Container for returned callback data.

    This is currently a dummy class into which urlgrabber can stuff
    information for passing to callbacks.  This way, the prototype for
    all callbacks is the same, regardless of the data that will be
    passed back.  Any function that accepts a callback function as an
    argument SHOULD document what it will define in this object.

    It is possible that this class will have some greater
    functionality in the future.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def urlgrab(url, filename=None, **kwargs):
    """grab the file at <url> and make a local copy at <filename>
    If filename is none, the basename of the url is used.
    urlgrab returns the filename of the local file, which may be different
    from the passed-in filename if the copy_local kwarg == 0.
    
    See module documentation for a description of possible kwargs.
    """
    return default_grabber.urlgrab(url, filename, **kwargs)

def urlopen(url, **kwargs):
    """open the url and return a file object
    If a progress object or throttle specifications exist, then
    a special file object will be returned that supports them.
    The file object can be treated like any other file object.
    
    See module documentation for a description of possible kwargs.
    """
    return default_grabber.urlopen(url, **kwargs)

def urlread(url, limit=None, **kwargs):
    """read the url into a string, up to 'limit' bytes
    If the limit is exceeded, an exception will be thrown.  Note that urlread
    is NOT intended to be used as a way of saying "I want the first N bytes"
    but rather 'read the whole file into memory, but don't use too much'
    
    See module documentation for a description of possible kwargs.
    """
    return default_grabber.urlread(url, limit, **kwargs)


class URLParser:
    """Process the URLs before passing them to urllib2.

    This class does several things:

      * add any prefix
      * translate a "raw" file to a proper file: url
      * handle any http or https auth that's encoded within the url
      * quote the url

    Only the "parse" method is called directly, and it calls sub-methods.

    An instance of this class is held in the options object, which
    means that it's easy to change the behavior by sub-classing and
    passing the replacement in.  It need only have a method like:

        url, parts = urlparser.parse(url, opts)
    """

    def parse(self, url, opts):
        """parse the url and return the (modified) url and its parts

        Note: a raw file WILL be quoted when it's converted to a URL.
        However, other urls (ones which come with a proper scheme) may
        or may not be quoted according to opts.quote

          opts.quote = 1     --> quote it
          opts.quote = 0     --> do not quote it
          opts.quote = None  --> guess
        """
        url = _to_utf8(url)
        quote = opts.quote
        
        if opts.prefix:
            url = self.add_prefix(url, opts.prefix)
            
        parts = urlparse.urlparse(url)
        (scheme, host, path, parm, query, frag) = parts

        if not scheme or (len(scheme) == 1 and scheme in string.letters):
            # if a scheme isn't specified, we guess that it's "file:"
            if url[0] not in '/\\': url = os.path.abspath(url)
            url = 'file:' + urllib.pathname2url(url)
            parts = urlparse.urlparse(url)
            quote = 0 # pathname2url quotes, so we won't do it again
            
        if scheme in ['http', 'https']:
            parts = self.process_http(parts, url)
            
        if quote is None:
            quote = self.guess_should_quote(parts)
        if quote:
            parts = self.quote(parts)
        
        url = urlparse.urlunparse(parts)
        return url, parts

    def add_prefix(self, url, prefix):
        if prefix[-1] == '/' or url[0] == '/':
            url = prefix + url
        else:
            url = prefix + '/' + url
        return url

    def process_http(self, parts, url):
        (scheme, host, path, parm, query, frag) = parts
        # TODO: auth-parsing here, maybe? pycurl doesn't really need it
        return (scheme, host, path, parm, query, frag)

    def quote(self, parts):
        """quote the URL

        This method quotes ONLY the path part.  If you need to quote
        other parts, you should override this and pass in your derived
        class.  The other alternative is to quote other parts before
        passing into urlgrabber.
        """
        (scheme, host, path, parm, query, frag) = parts
        path = urllib.quote(path)
        return (scheme, host, path, parm, query, frag)

    hexvals = '0123456789ABCDEF'
    def guess_should_quote(self, parts):
        """
        Guess whether we should quote a path.  This amounts to
        guessing whether it's already quoted.

        find ' '   ->  1
        find '%'   ->  1
        find '%XX' ->  0
        else       ->  1
        """
        (scheme, host, path, parm, query, frag) = parts
        if ' ' in path:
            return 1
        ind = string.find(path, '%')
        if ind > -1:
            while ind > -1:
                if len(path) < ind+3:
                    return 1
                code = path[ind+1:ind+3].upper()
                if     code[0] not in self.hexvals or \
                       code[1] not in self.hexvals:
                    return 1
                ind = string.find(path, '%', ind+1)
            return 0
        return 1
    
class URLGrabberOptions:
    """Class to ease kwargs handling."""

    def __init__(self, delegate=None, **kwargs):
        """Initialize URLGrabberOptions object.
        Set default values for all options and then update options specified
        in kwargs.
        """
        self.delegate = delegate
        if delegate is None:
            self._set_defaults()
        self._set_attributes(**kwargs)
    
    def __getattr__(self, name):
        if self.delegate and hasattr(self.delegate, name):
            return getattr(self.delegate, name)
        raise AttributeError, name
    
    def raw_throttle(self):
        """Calculate raw throttle value from throttle and bandwidth 
        values.
        """
        if self.throttle <= 0:  
            return 0
        elif type(self.throttle) == type(0): 
            return float(self.throttle)
        else: # throttle is a float
            return self.bandwidth * self.throttle
        
    def find_proxy(self, url, scheme):
        """Find the proxy to use for this URL.
        Use the proxies dictionary first, then libproxy.
        """
        self.proxy = None
        if scheme not in ('ftp', 'http', 'https'):
            return

        if self.proxies:
            proxy = self.proxies.get(scheme)
            if proxy is None:
                if scheme == 'http':
                    proxy = self.proxies.get('https')
                elif scheme == 'https':
                    proxy = self.proxies.get('http')
            if proxy == '_none_':
                proxy = ''
            self.proxy = proxy
            return

        if self.libproxy:
            global _libproxy_cache
            if _libproxy_cache is None:
                try:
                    import libproxy
                    _libproxy_cache = libproxy.ProxyFactory()
                except:
                    _libproxy_cache = False
            if _libproxy_cache:
                for proxy in _libproxy_cache.getProxies(url):
                    if proxy.startswith('http://'):
                        if DEBUG: DEBUG.info('using proxy "%s" for url %s' % (proxy, url))
                        self.proxy = proxy
                        break

    def derive(self, **kwargs):
        """Create a derived URLGrabberOptions instance.
        This method creates a new instance and overrides the
        options specified in kwargs.
        """
        return URLGrabberOptions(delegate=self, **kwargs)
        
    def _set_attributes(self, **kwargs):
        """Update object attributes with those provided in kwargs."""
        self.__dict__.update(kwargs)
        if kwargs.has_key('range'):
            # normalize the supplied range value
            self.range = range_tuple_normalize(self.range)
        if not self.reget in [None, 'simple', 'check_timestamp']:
            raise URLGrabError(11, _('Illegal reget mode: %s') \
                               % (self.reget, ))

    def _set_defaults(self):
        """Set all options to their default values. 
        When adding new options, make sure a default is
        provided here.
        """
        self.progress_obj = None
        self.multi_progress_obj = None
        self.throttle = 1.0
        self.bandwidth = 0
        self.retry = None
        self.retrycodes = [-1,2,4,5,6,7]
        self.checkfunc = None
        self.failfunc = _do_raise
        self.copy_local = 0
        self.close_connection = 0
        self.range = None
        self.user_agent = 'urlgrabber/%s' % __version__
        self.ip_resolve = None
        self.keepalive = 1
        self.proxies = None
        self.libproxy = False
        self.proxy = None
        self.reget = None
        self.failure_callback = None
        self.interrupt_callback = None
        self.prefix = None
        self.opener = None
        self.cache_openers = True
        self.timeout = 300
        self.minrate = None
        self.text = None
        self.http_headers = None
        self.ftp_headers = None
        self.data = None
        self.urlparser = URLParser()
        self.quote = None
        self.username = None
        self.password = None
        self.ssl_ca_cert = None # sets SSL_CAINFO - path to certdb
        self.ssl_context = None # no-op in pycurl
        self.ssl_verify_peer = True # check peer's cert for authenticityb
        self.ssl_verify_host = True # make sure who they are and who the cert is for matches
        self.ssl_key = None # client key
        self.ssl_key_type = 'PEM' #(or DER)
        self.ssl_cert = None # client cert
        self.ssl_cert_type = 'PEM' # (or DER)
        self.ssl_key_pass = None # password to access the key
        self.size = None # if we know how big the thing we're getting is going
                         # to be. this is ultimately a MAXIMUM size for the file
        self.max_header_size = 2097152 #2mb seems reasonable for maximum header size
        self.async = None # blocking by default
        self.mirror_group = None
        self.max_connections = 5
        self.timedhosts = None
        self.half_life = 30*24*60*60 # 30 days
        self.default_speed = 500e3 # 500 kBps
        self.ftp_disable_epsv = False
        
    def __repr__(self):
        return self.format()
        
    def format(self, indent='  '):
        keys = self.__dict__.keys()
        if self.delegate is not None:
            keys.remove('delegate')
        keys.sort()
        s = '{\n'
        for k in keys:
            s = s + indent + '%-15s: %s,\n' % \
                (repr(k), repr(self.__dict__[k]))
        if self.delegate:
            df = self.delegate.format(indent + '  ')
            s = s + indent + '%-15s: %s\n' % ("'delegate'", df)
        s = s + indent + '}'
        return s

def _do_raise(obj):
    raise obj.exception

def _run_callback(cb, obj):
    if not cb:
        return
    if callable(cb):
        return cb(obj)
    cb, arg, karg = cb
    return cb(obj, *arg, **karg)

class URLGrabber(object):
    """Provides easy opening of URLs with a variety of options.
    
    All options are specified as kwargs. Options may be specified when
    the class is created and may be overridden on a per request basis.
    
    New objects inherit default values from default_grabber.
    """
    
    def __init__(self, **kwargs):
        self.opts = URLGrabberOptions(**kwargs)
    
    def _retry(self, opts, func, *args):
        tries = 0
        while 1:
            # there are only two ways out of this loop.  The second has
            # several "sub-ways"
            #   1) via the return in the "try" block
            #   2) by some exception being raised
            #      a) an excepton is raised that we don't "except"
            #      b) a callback raises ANY exception
            #      c) we're not retry-ing or have run out of retries
            #      d) the URLGrabError code is not in retrycodes
            # beware of infinite loops :)
            tries = tries + 1
            exception = None
            callback  = None
            if DEBUG: DEBUG.info('attempt %i/%s: %s',
                                 tries, opts.retry, args[0])
            try:
                r = apply(func, (opts,) + args, {})
                if DEBUG: DEBUG.info('success')
                return r
            except URLGrabError, e:
                exception = e
                callback = opts.failure_callback
            except KeyboardInterrupt, e:
                exception = e
                callback = opts.interrupt_callback
                if not callback:
                    raise

            if DEBUG: DEBUG.info('exception: %s', exception)
            if callback:
                if DEBUG: DEBUG.info('calling callback: %s', callback)
                obj = CallbackObject(exception=exception, url=args[0],
                                     tries=tries, retry=opts.retry)
                _run_callback(callback, obj)

            if (opts.retry is None) or (tries == opts.retry):
                if DEBUG: DEBUG.info('retries exceeded, re-raising')
                raise

            retrycode = getattr(exception, 'errno', None)
            if (retrycode is not None) and (retrycode not in opts.retrycodes):
                if DEBUG: DEBUG.info('retrycode (%i) not in list %s, re-raising',
                                     retrycode, opts.retrycodes)
                raise
    
    def urlopen(self, url, opts=None, **kwargs):
        """open the url and return a file object
        If a progress object or throttle value specified when this 
        object was created, then  a special file object will be 
        returned that supports them. The file object can be treated 
        like any other file object.
        """
        url = _to_utf8(url)
        opts = (opts or self.opts).derive(**kwargs)
        if DEBUG: DEBUG.debug('combined options: %s' % repr(opts))
        (url,parts) = opts.urlparser.parse(url, opts) 
        opts.find_proxy(url, parts[0])
        def retryfunc(opts, url):
            return PyCurlFileObject(url, filename=None, opts=opts)
        return self._retry(opts, retryfunc, url)
    
    def urlgrab(self, url, filename=None, opts=None, **kwargs):
        """grab the file at <url> and make a local copy at <filename>
        If filename is none, the basename of the url is used.
        urlgrab returns the filename of the local file, which may be 
        different from the passed-in filename if copy_local == 0.
        """
        url = _to_utf8(url)
        opts = (opts or self.opts).derive(**kwargs)
        if DEBUG: DEBUG.debug('combined options: %s' % repr(opts))
        (url,parts) = opts.urlparser.parse(url, opts) 
        (scheme, host, path, parm, query, frag) = parts
        opts.find_proxy(url, scheme)
        if filename is None:
            filename = os.path.basename( urllib.unquote(path) )
            if not filename:
                # This is better than nothing.
                filename = 'index.html'
        if scheme == 'file' and not opts.copy_local:
            # just return the name of the local file - don't make a 
            # copy currently
            path = urllib.url2pathname(path)
            if host:
                path = os.path.normpath('//' + host + path)
            if not os.path.exists(path):
                err = URLGrabError(2, 
                      _('Local file does not exist: %s') % (path, ))
                err.url = url
                raise err
            elif not os.path.isfile(path):
                err = URLGrabError(3, 
                                 _('Not a normal file: %s') % (path, ))
                err.url = url
                raise err

            elif not opts.range:
                if not opts.checkfunc is None:
                    obj = CallbackObject(filename=path, url=url)
                    _run_callback(opts.checkfunc, obj)
                return path
        
        if opts.async:
            opts.url = url
            opts.filename = filename
            opts.size = int(opts.size or 0)
            _async_queue.append(opts)
            return filename

        def retryfunc(opts, url, filename):
            fo = PyCurlFileObject(url, filename, opts)
            try:
                fo._do_grab()
                if fo._tm_last:
                    dlsz = fo._tm_last[0] - fo._tm_first[0]
                    dltm = fo._tm_last[1] - fo._tm_first[1]
                    _TH.update(url, dlsz, dltm, None)
                if not opts.checkfunc is None:
                    obj = CallbackObject(filename=filename, url=url)
                    _run_callback(opts.checkfunc, obj)
            finally:
                fo.close()
            return filename
        
        try:
            return self._retry(opts, retryfunc, url, filename)
        except URLGrabError, e:
            _TH.update(url, 0, 0, e)
            opts.exception = e
            return _run_callback(opts.failfunc, opts)
    
    def urlread(self, url, limit=None, opts=None, **kwargs):
        """read the url into a string, up to 'limit' bytes
        If the limit is exceeded, an exception will be thrown.  Note
        that urlread is NOT intended to be used as a way of saying 
        "I want the first N bytes" but rather 'read the whole file 
        into memory, but don't use too much'
        """
        url = _to_utf8(url)
        opts = (opts or self.opts).derive(**kwargs)
        if DEBUG: DEBUG.debug('combined options: %s' % repr(opts))
        (url,parts) = opts.urlparser.parse(url, opts) 
        opts.find_proxy(url, parts[0])
        if limit is not None:
            limit = limit + 1
            
        def retryfunc(opts, url, limit):
            fo = PyCurlFileObject(url, filename=None, opts=opts)
            s = ''
            try:
                # this is an unfortunate thing.  Some file-like objects
                # have a default "limit" of None, while the built-in (real)
                # file objects have -1.  They each break the other, so for
                # now, we just force the default if necessary.
                if limit is None: s = fo.read()
                else: s = fo.read(limit)

                if not opts.checkfunc is None:
                    obj = CallbackObject(data=s, url=url)
                    _run_callback(opts.checkfunc, obj)
            finally:
                fo.close()
            return s
            
        s = self._retry(opts, retryfunc, url, limit)
        if limit and len(s) > limit:
            err = URLGrabError(8, 
                               _('Exceeded limit (%i): %s') % (limit, url))
            err.url = url
            raise err

        return s
        
    def _make_callback(self, callback_obj):
        # not used, left for compatibility
        if callable(callback_obj):
            return callback_obj, (), {}
        else:
            return callback_obj

# create the default URLGrabber used by urlXXX functions.
# NOTE: actual defaults are set in URLGrabberOptions
default_grabber = URLGrabber()


class PyCurlFileObject(object):
    def __init__(self, url, filename, opts):
        self.fo = None
        self._hdr_dump = ''
        self._parsed_hdr = None
        self.url = url
        self.scheme = urlparse.urlsplit(self.url)[0]
        self.filename = filename
        self.append = False
        self.reget_time = None
        self.opts = opts
        if self.opts.reget == 'check_timestamp':
            raise NotImplementedError, "check_timestamp regets are not implemented in this ver of urlgrabber. Please report this."
        self._complete = False
        self._rbuf = ''
        self._rbufsize = 1024*8
        self._ttime = time.time()
        self._tsize = 0
        self._amount_read = 0
        self._reget_length = 0
        self._range = None
        self._prog_running = False
        self._error = (None, None)
        self.size = 0
        self._hdr_ended = False
        self._tm_first = None
        self._tm_last = None
        self._do_open()
        

    def __getattr__(self, name):
        """This effectively allows us to wrap at the instance level.
        Any attribute not found in _this_ object will be searched for
        in self.fo.  This includes methods."""

        if hasattr(self.fo, name):
            return getattr(self.fo, name)
        raise AttributeError, name

    def _retrieve(self, buf):
        try:
            tm = self._amount_read + len(buf), time.time()
            if self._tm_first is None:
                self._tm_first = tm
            else:
                self._tm_last = tm

            if not self._prog_running:
                if self.opts.progress_obj:
                    size  = self.size + self._reget_length
                    self.opts.progress_obj.start(self._prog_reportname, 
                                                 urllib.unquote(self.url), 
                                                 self._prog_basename, 
                                                 size=size,
                                                 text=self.opts.text)
                    self._prog_running = True
                    self.opts.progress_obj.update(self._amount_read)

            self._amount_read += len(buf)
            try:
                if self._range:
                    # client-side ranges
                    pos = self._amount_read - len(buf)
                    start = self._range[0] - pos
                    stop = self._range[1] - pos
                    if start < len(buf) and stop > 0:
                        self.fo.write(buf[max(start, 0):stop])
                else:
                    self.fo.write(buf)
            except IOError, e:
                self._cb_error = URLGrabError(16, exception2msg(e))
                return -1
            return len(buf)
        except KeyboardInterrupt:
            return -1
            
    def _hdr_retrieve(self, buf):
        if self._hdr_ended:
            self._hdr_dump = ''
            self.size = 0
            self._hdr_ended = False

        if self._over_max_size(cur=len(self._hdr_dump), 
                               max_size=self.opts.max_header_size):
            return -1
        try:
            # we have to get the size before we do the progress obj start
            # but we can't do that w/o making it do 2 connects, which sucks
            # so we cheat and stuff it in here in the hdr_retrieve
            if self.scheme in ['http','https']:
                if buf.lower().find('content-length:') != -1:
                    length = buf.split(':')[1]
                    self.size = int(length)
                elif (self.append or self.opts.range) and self._hdr_dump == '' and ' 200 ' in buf:
                    # reget was attempted but server sends it all
                    # undo what we did in _build_range()
                    self.append = False
                    self.reget_time = None
                    self._amount_read = 0
                    self._reget_length = 0
                    self._range = self.opts.range
                    self.fo.truncate(0)
            elif self.scheme in ['ftp']:
                s = None
                if buf.startswith('213 '):
                    s = buf[3:].strip()
                    if len(s) >= 14:
                        s = None # ignore MDTM responses
                elif buf.startswith('150 '):
                    s = parse150(buf)
                if s:
                    self.size = int(s)
                    
            if buf.lower().find('location') != -1:
                location = ':'.join(buf.split(':')[1:])
                location = location.strip()
                self.scheme = urlparse.urlsplit(location)[0]
                self.url = location
                
            self._hdr_dump += buf
            if len(self._hdr_dump) != 0 and buf == '\r\n':
                self._hdr_ended = True
                if DEBUG: DEBUG.debug('header ended:')
                
            return len(buf)
        except KeyboardInterrupt:
            return pycurl.READFUNC_ABORT

    def _return_hdr_obj(self):
        if self._parsed_hdr:
            return self._parsed_hdr
        statusend = self._hdr_dump.find('\n')
        statusend += 1 # ridiculous as it may seem.
        hdrfp = StringIO()
        hdrfp.write(self._hdr_dump[statusend:])
        hdrfp.seek(0)
        self._parsed_hdr =  mimetools.Message(hdrfp)
        return self._parsed_hdr
    
    hdr = property(_return_hdr_obj)
    http_code = property(fget=
                 lambda self: self.curl_obj.getinfo(pycurl.RESPONSE_CODE))

    def _set_opts(self, opts={}):
        # XXX
        if not opts:
            opts = self.opts

        # keepalives
        if not opts.keepalive:
            self.curl_obj.setopt(pycurl.FORBID_REUSE, 1)

        # defaults we're always going to set
        self.curl_obj.setopt(pycurl.NOPROGRESS, False)
        self.curl_obj.setopt(pycurl.NOSIGNAL, True)
        self.curl_obj.setopt(pycurl.WRITEFUNCTION, self._retrieve)
        self.curl_obj.setopt(pycurl.HEADERFUNCTION, self._hdr_retrieve)
        self.curl_obj.setopt(pycurl.PROGRESSFUNCTION, self._progress_update)
        self.curl_obj.setopt(pycurl.FAILONERROR, True)
        self.curl_obj.setopt(pycurl.OPT_FILETIME, True)
        self.curl_obj.setopt(pycurl.FOLLOWLOCATION, False)
        
        if DEBUG and DEBUG.level <= 10:
            self.curl_obj.setopt(pycurl.VERBOSE, True)
        if opts.user_agent:
            self.curl_obj.setopt(pycurl.USERAGENT, opts.user_agent)
        if opts.ip_resolve:
            # Default is: IPRESOLVE_WHATEVER
            ipr = opts.ip_resolve.lower()
            if ipr == 'whatever': # Do we need this?
                self.curl_obj.setopt(pycurl.IPRESOLVE,pycurl.IPRESOLVE_WHATEVER)
            if ipr == 'ipv4':
                self.curl_obj.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)
            if ipr == 'ipv6':
                self.curl_obj.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V6)
        
        # maybe to be options later
        self.curl_obj.setopt(pycurl.FOLLOWLOCATION, False)
        self.curl_obj.setopt(pycurl.MAXREDIRS, 5)
        
        # timeouts
        timeout = 300
        if hasattr(opts, 'timeout'):
            timeout = int(opts.timeout or 0)
        self.curl_obj.setopt(pycurl.CONNECTTIMEOUT, timeout)
        self.curl_obj.setopt(pycurl.LOW_SPEED_LIMIT, opts.minrate or 1000)
        self.curl_obj.setopt(pycurl.LOW_SPEED_TIME, timeout)

        # ssl options
        if self.scheme == 'https':
            if opts.ssl_ca_cert: # this may do ZERO with nss  according to curl docs
                self.curl_obj.setopt(pycurl.CAPATH, opts.ssl_ca_cert)
                self.curl_obj.setopt(pycurl.CAINFO, opts.ssl_ca_cert)
            self.curl_obj.setopt(pycurl.SSL_VERIFYPEER, opts.ssl_verify_peer)
            if opts.ssl_verify_host: # 1 is meaningless to curl
                self.curl_obj.setopt(pycurl.SSL_VERIFYHOST, 2)
            if opts.ssl_key:
                self.curl_obj.setopt(pycurl.SSLKEY, opts.ssl_key)
            if opts.ssl_key_type:
                self.curl_obj.setopt(pycurl.SSLKEYTYPE, opts.ssl_key_type)
            if opts.ssl_cert:
                self.curl_obj.setopt(pycurl.SSLCERT, opts.ssl_cert)
                # if we have a client side cert - turn off reuse b/c nss is odd
                self.curl_obj.setopt(pycurl.FORBID_REUSE, 1)
            if opts.ssl_cert_type:                
                self.curl_obj.setopt(pycurl.SSLCERTTYPE, opts.ssl_cert_type)
            if opts.ssl_key_pass:
                self.curl_obj.setopt(pycurl.SSLKEYPASSWD, opts.ssl_key_pass)

        #headers:
        if opts.http_headers and self.scheme in ('http', 'https'):
            headers = []
            for (tag, content) in opts.http_headers:
                headers.append('%s:%s' % (tag, content))
            self.curl_obj.setopt(pycurl.HTTPHEADER, headers)

        # ranges:
        if opts.range or opts.reget:
            range_str = self._build_range()
            if range_str:
                self.curl_obj.setopt(pycurl.RANGE, range_str)
            
        # throttle/bandwidth
        if hasattr(opts, 'raw_throttle') and opts.raw_throttle():
            self.curl_obj.setopt(pycurl.MAX_RECV_SPEED_LARGE, int(opts.raw_throttle()))
            
        # proxy
        if opts.proxy is not None:
            self.curl_obj.setopt(pycurl.PROXY, opts.proxy)
            self.curl_obj.setopt(pycurl.PROXYAUTH,
                # All but Kerberos.  BZ 769254
                pycurl.HTTPAUTH_ANY - pycurl.HTTPAUTH_GSSNEGOTIATE)

        if opts.username and opts.password:
            if self.scheme in ('http', 'https'):
                self.curl_obj.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_ANY)

            if opts.username and opts.password:
                # apparently when applying them as curlopts they do not require quoting of any kind
                userpwd = '%s:%s' % (opts.username, opts.password)
                self.curl_obj.setopt(pycurl.USERPWD, userpwd)

        #posts - simple - expects the fields as they are
        if opts.data:
            self.curl_obj.setopt(pycurl.POST, True)
            self.curl_obj.setopt(pycurl.POSTFIELDS, _to_utf8(opts.data))

        # ftp
        if opts.ftp_disable_epsv:
            self.curl_obj.setopt(pycurl.FTP_USE_EPSV, False)

        # our url
        self.curl_obj.setopt(pycurl.URL, self.url)
        
    
    def _do_perform(self):
        if self._complete:
            return
        
        try:
            self.curl_obj.perform()
        except pycurl.error, e:
            # XXX - break some of these out a bit more clearly
            # to other URLGrabErrors from 
            # http://curl.haxx.se/libcurl/c/libcurl-errors.html
            # this covers e.args[0] == 22 pretty well - which will be common
            
            code = self.http_code
            errcode = e.args[0]
            errurl = urllib.unquote(self.url)
            
            if self._error[0]:
                errcode = self._error[0]
                
            if errcode == 23 and 200 <= code <= 299:
                # this is probably wrong but ultimately this is what happens
                # we have a legit http code and a pycurl 'writer failed' code
                # which almost always means something aborted it from outside
                # since we cannot know what it is -I'm banking on it being
                # a ctrl-c. XXXX - if there's a way of going back two raises to 
                # figure out what aborted the pycurl process FIXME
                raise getattr(self, '_cb_error', KeyboardInterrupt)
            
            elif errcode == 28:
                err = URLGrabError(12, _('Timeout on %s: %s') % (errurl, e))
                err.url = errurl
                raise err
                
            elif errcode == 42:
                # this is probably wrong but ultimately this is what happens
                # we have a legit http code and a pycurl 'writer failed' code
                # which almost always means something aborted it from outside
                # since we cannot know what it is -I'm banking on it being
                # a ctrl-c. XXXX - if there's a way of going back two raises to 
                # figure out what aborted the pycurl process FIXME
                raise KeyboardInterrupt
                
            else:
                pyerr2str = { 5 : _("Couldn't resolve proxy"),
                              6 : _("Couldn't resolve host"),
                              7 : _("Couldn't connect"),
                              8 : _("Bad reply to FTP server"),
                              9 : _("Access denied"),
                             11 : _("Bad reply to FTP pass"),
                             13 : _("Bad reply to FTP pasv"),
                             14 : _("Bad reply to FTP 227"),
                             15 : _("Couldn't get FTP host"),
                             17 : _("Couldn't set FTP type"),
                             18 : _("Partial file"),
                             19 : _("FTP RETR command failed"),
                             22 : _("HTTP returned error"),
                             23 : _("Write error"),
                             25 : _("Upload failed"),
                             26 : _("Read error"),
                             27 : _("Out of Memory"),
                             28 : _("Operation timed out"),
                             30 : _("FTP PORT command failed"),
                             31 : _("FTP REST command failed"),
                             33 : _("Range failed"),
                             34 : _("HTTP POST failed"),
                             35 : _("SSL CONNECT failed"),
                             36 : _("Couldn't resume download"),
                             37 : _("Couldn't read file"),
                             42 : _("Aborted by callback"),
                             47 : _("Too many redirects"),
                             51 : _("Peer certificate failed verification"),
                             52 : _("Got nothing: SSL certificate expired?"),
                             53 : _("SSL engine not found"),
                             54 : _("SSL engine set failed"),
                             55 : _("Network error send()"),
                             56 : _("Network error recv()"),
                             58 : _("Local certificate failed"),
                             59 : _("SSL set cipher failed"),
                             60 : _("Local CA certificate failed"),
                             61 : _("HTTP bad transfer encoding"),
                             63 : _("Maximum file size exceeded"),
                             64 : _("FTP SSL failed"),
                             67 : _("Authentication failure"),
                             70 : _("Out of disk space on server"),
                             73 : _("Remove file exists"),
                              }
                errstr = str(e.args[1]) or pyerr2str.get(errcode, '<Unknown>')
                if code and not 200 <= code <= 299:
                    msg = '%s Error %d - %s' % (self.scheme.upper(), code,
                                                self.scheme in ('http', 'https')
                                                and responses.get(code) or errstr)
                else:
                    msg = 'curl#%s - "%s"' % (errcode, errstr)
                    code = errcode

                err = URLGrabError(14, msg)
                err.url = errurl
                err.code = code
                raise err

        else:
            if self._error[1]:
                msg = self._error[1]
                err = URLGrabError(14, msg)
                err.url = urllib.unquote(self.url)
                raise err

    def _do_open(self):
        self.curl_obj = _curl_cache
        self.curl_obj.reset() # reset all old settings away, just in case
        # setup any ranges
        self._set_opts()
        self._do_grab()
        return self.fo

    def _add_headers(self):
        pass
        
    def _build_range(self):
        reget_length = 0
        rt = None
        if self.opts.reget and type(self.filename) in types.StringTypes:
            # we have reget turned on and we're dumping to a file
            try:
                s = os.stat(self.filename)
            except OSError:
                pass
            else:
                self.reget_time = s[stat.ST_MTIME]
                reget_length = s[stat.ST_SIZE]

                # Set initial length when regetting
                self._amount_read = reget_length    
                self._reget_length = reget_length # set where we started from, too

                rt = reget_length, ''
                self.append = 1
                
        if self.opts.range:
            rt = self.opts.range
            
            if rt[0] is None:
                rt = (0, rt[1])
            rt = (rt[0] + reget_length, rt[1])
            

        if rt:
            header = range_tuple_to_header(rt)
            if header:
                return header.split('=')[1]



    def _make_request(self, req, opener):
        #XXXX
        # This doesn't do anything really, but we could use this
        # instead of do_open() to catch a lot of crap errors as 
        # mstenner did before here
        return (self.fo, self.hdr)
        
        try:
            if self.opts.timeout:
                old_to = socket.getdefaulttimeout()
                socket.setdefaulttimeout(self.opts.timeout)
                try:
                    fo = opener.open(req)
                finally:
                    socket.setdefaulttimeout(old_to)
            else:
                fo = opener.open(req)
            hdr = fo.info()
        except ValueError, e:
            err = URLGrabError(1, _('Bad URL: %s : %s') % (self.url, e, ))
            err.url = self.url
            raise err

        except RangeError, e:
            err = URLGrabError(9, _('%s on %s') % (e, self.url))
            err.url = self.url
            raise err
        except urllib2.HTTPError, e:
            new_e = URLGrabError(14, _('%s on %s') % (e, self.url))
            new_e.code = e.code
            new_e.exception = e
            new_e.url = self.url
            raise new_e
        except IOError, e:
            if hasattr(e, 'reason') and isinstance(e.reason, socket.timeout):
                err = URLGrabError(12, _('Timeout on %s: %s') % (self.url, e))
                err.url = self.url
                raise err
            else:
                err = URLGrabError(4, _('IOError on %s: %s') % (self.url, e))
                err.url = self.url
                raise err

        except OSError, e:
            err = URLGrabError(5, _('%s on %s') % (e, self.url))
            err.url = self.url
            raise err

        except HTTPException, e:
            err = URLGrabError(7, _('HTTP Exception (%s) on %s: %s') % \
                            (e.__class__.__name__, self.url, e))
            err.url = self.url
            raise err

        else:
            return (fo, hdr)
        
    def _do_grab(self):
        """dump the file to a filename or StringIO buffer"""

        if self._complete:
            return
        _was_filename = False
        if type(self.filename) in types.StringTypes and self.filename:
            _was_filename = True
            self._prog_reportname = str(self.filename)
            self._prog_basename = os.path.basename(self.filename)
            
            if self.append: mode = 'ab'
            else: mode = 'wb'

            if DEBUG: DEBUG.info('opening local file "%s" with mode %s' % \
                                 (self.filename, mode))
            try:
                self.fo = open(self.filename, mode)
            except IOError, e:
                err = URLGrabError(16, _(\
                  'error opening local file from %s, IOError: %s') % (self.url, e))
                err.url = self.url
                raise err

        else:
            self._prog_reportname = 'MEMORY'
            self._prog_basename = 'MEMORY'

            
            self.fo = StringIO()
            # if this is to be a tempfile instead....
            # it just makes crap in the tempdir
            #fh, self._temp_name = mkstemp()
            #self.fo = open(self._temp_name, 'wb')

        try:            
            self._do_perform()
        except URLGrabError, e:
            self.fo.flush()
            self.fo.close()
            raise e
    
        if _was_filename:
            # close it up
            self.fo.flush()
            self.fo.close()

            # Set the URL where we got it from:
            if xattr is not None:
                # See: http://www.freedesktop.org/wiki/CommonExtendedAttributes
                try:
                    xattr.set(self.filename, 'user.xdg.origin.url', self.url)
                except:
                    pass # URL too long. = IOError ... ignore everything.

            # set the time
            mod_time = self.curl_obj.getinfo(pycurl.INFO_FILETIME)
            if mod_time != -1:
                try:
                    os.utime(self.filename, (mod_time, mod_time))
                except OSError, e:
                    err = URLGrabError(16, _(\
                      'error setting timestamp on file %s from %s, OSError: %s') 
                              % (self.filename, self.url, e))
                    err.url = self.url
                    raise err
            # re open it
            try:
                self.fo = open(self.filename, 'r')
            except IOError, e:
                err = URLGrabError(16, _(\
                  'error opening file from %s, IOError: %s') % (self.url, e))
                err.url = self.url
                raise err
                
        else:
            #self.fo = open(self._temp_name, 'r')
            self.fo.seek(0)

        self._complete = True
    
    def _fill_buffer(self, amt=None):
        """fill the buffer to contain at least 'amt' bytes by reading
        from the underlying file object.  If amt is None, then it will
        read until it gets nothing more.  It updates the progress meter
        and throttles after every self._rbufsize bytes."""
        # the _rbuf test is only in this first 'if' for speed.  It's not
        # logically necessary
        if self._rbuf and not amt is None:
            L = len(self._rbuf)
            if amt > L:
                amt = amt - L
            else:
                return

        # if we've made it here, then we don't have enough in the buffer
        # and we need to read more.
        
        if not self._complete: self._do_grab() #XXX cheater - change on ranges
        
        buf = [self._rbuf]
        bufsize = len(self._rbuf)
        while amt is None or amt:
            # first, delay if necessary for throttling reasons
            if self.opts.raw_throttle():
                diff = self._tsize/self.opts.raw_throttle() - \
                       (time.time() - self._ttime)
                if diff > 0: time.sleep(diff)
                self._ttime = time.time()
                
            # now read some data, up to self._rbufsize
            if amt is None: readamount = self._rbufsize
            else:           readamount = min(amt, self._rbufsize)
            try:
                new = self.fo.read(readamount)
            except socket.error, e:
                err = URLGrabError(4, _('Socket Error on %s: %s') % (self.url, e))
                err.url = self.url
                raise err

            except socket.timeout, e:
                raise URLGrabError(12, _('Timeout on %s: %s') % (self.url, e))
                err.url = self.url
                raise err

            except IOError, e:
                raise URLGrabError(4, _('IOError on %s: %s') %(self.url, e))
                err.url = self.url
                raise err

            newsize = len(new)
            if not newsize: break # no more to read

            if amt: amt = amt - newsize
            buf.append(new)
            bufsize = bufsize + newsize
            self._tsize = newsize
            self._amount_read = self._amount_read + newsize
            #if self.opts.progress_obj:
            #    self.opts.progress_obj.update(self._amount_read)

        self._rbuf = string.join(buf, '')
        return

    def _progress_update(self, download_total, downloaded, upload_total, uploaded):
        if self._over_max_size(cur=self._amount_read-self._reget_length):
            return -1

        try:
            if self._prog_running:
                downloaded += self._reget_length
                self.opts.progress_obj.update(downloaded)
        except (KeyboardInterrupt, IOError):
            return -1
    
    def _over_max_size(self, cur, max_size=None):

        if not max_size:
            if not self.opts.size:
                max_size = self.size
            else:
                max_size = self.opts.size

        if not max_size: return False # if we have None for all of the Max then this is dumb

        if cur > int(float(max_size) * 1.10):

            msg = _("Downloaded more than max size for %s: %s > %s") \
                        % (self.url, cur, max_size)
            self._error = (pycurl.E_FILESIZE_EXCEEDED, msg)
            return True
        return False
        
    def read(self, amt=None):
        self._fill_buffer(amt)
        if amt is None:
            s, self._rbuf = self._rbuf, ''
        else:
            s, self._rbuf = self._rbuf[:amt], self._rbuf[amt:]
        return s

    def readline(self, limit=-1):
        if not self._complete: self._do_grab()
        return self.fo.readline()
        
        i = string.find(self._rbuf, '\n')
        while i < 0 and not (0 < limit <= len(self._rbuf)):
            L = len(self._rbuf)
            self._fill_buffer(L + self._rbufsize)
            if not len(self._rbuf) > L: break
            i = string.find(self._rbuf, '\n', L)

        if i < 0: i = len(self._rbuf)
        else: i = i+1
        if 0 <= limit < len(self._rbuf): i = limit

        s, self._rbuf = self._rbuf[:i], self._rbuf[i:]
        return s

    def close(self):
        if self._prog_running:
            self.opts.progress_obj.end(self._amount_read)
        self.fo.close()
        
    def geturl(self):
        """ Provide the geturl() method, used to be got from
            urllib.addinfourl, via. urllib.URLopener.* """
        return self.url
        
if hasattr(pycurl, 'GLOBAL_ACK_EINTR'):
    # fail immediately on ctrl-c
    pycurl.global_init(pycurl.GLOBAL_DEFAULT | pycurl.GLOBAL_ACK_EINTR)
_curl_cache = pycurl.Curl() # make one and reuse it over and over and over

def reset_curl_obj():
    """To make sure curl has reread the network/dns info we force a reload"""
    global _curl_cache
    _curl_cache.close()
    _curl_cache = pycurl.Curl()

_libproxy_cache = None
    

#####################################################################
# DEPRECATED FUNCTIONS
def set_throttle(new_throttle):
    """Deprecated. Use: default_grabber.throttle = new_throttle"""
    default_grabber.throttle = new_throttle

def set_bandwidth(new_bandwidth):
    """Deprecated. Use: default_grabber.bandwidth = new_bandwidth"""
    default_grabber.bandwidth = new_bandwidth

def set_progress_obj(new_progress_obj):
    """Deprecated. Use: default_grabber.progress_obj = new_progress_obj"""
    default_grabber.progress_obj = new_progress_obj

def set_user_agent(new_user_agent):
    """Deprecated. Use: default_grabber.user_agent = new_user_agent"""
    default_grabber.user_agent = new_user_agent
    
def retrygrab(url, filename=None, copy_local=0, close_connection=0,
              progress_obj=None, throttle=None, bandwidth=None,
              numtries=3, retrycodes=[-1,2,4,5,6,7], checkfunc=None):
    """Deprecated. Use: urlgrab() with the retry arg instead"""
    kwargs = {'copy_local' :  copy_local, 
              'close_connection' : close_connection,
              'progress_obj' : progress_obj, 
              'throttle' : throttle, 
              'bandwidth' : bandwidth,
              'retry' : numtries,
              'retrycodes' : retrycodes,
              'checkfunc' : checkfunc 
              }
    return urlgrab(url, filename, **kwargs)

        
#####################################################################
#  Serializer + parser: A replacement of the rather bulky Json code.
#
# - handles basic python literals, lists and tuples.
# - serialized strings never contain ' ' or '\n'
#
#####################################################################

_quoter_map = {}
for c in '%[(,)] \n':
    _quoter_map[c] = '%%%02x' % ord(c)
del c

def _dumps(v):
    if v is None: return 'None'
    if v is True: return 'True'
    if v is False: return 'False'
    if type(v) in (int, long, float):
        return str(v)
    if type(v) == unicode:
        v = v.encode('UTF8')
    if type(v) == str:
        def quoter(c): return _quoter_map.get(c, c)
        return "'%s'" % ''.join(map(quoter, v))
    if type(v) == tuple:
        return "(%s)" % ','.join(map(_dumps, v))
    if type(v) == list:
        return "[%s]" % ','.join(map(_dumps, v))
    raise TypeError, 'Can\'t serialize %s' % v

def _loads(s):
    def decode(v):
        if v == 'None': return None
        if v == 'True': return True
        if v == 'False': return False
        try: return int(v)
        except ValueError: pass
        try: return float(v)
        except ValueError: pass
        if len(v) >= 2 and v[0] == v[-1] == "'":
            ret = []; i = 1
            while True:
                j = v.find('%', i)
                ret.append(v[i:j]) # skips the final "'"
                if j == -1: break
                ret.append(chr(int(v[j + 1:j + 3], 16)))
                i = j + 3
            v = ''.join(ret)
        return v
    stk = None
    l = []
    i = j = 0
    while True:
        if j == len(s) or s[j] in ',)]':
            if j > i:
                l.append(decode(s[i:j]))
            if j == len(s): break
            if s[j] in ')]':
                if s[j] == ')':
                    l = tuple(l)
                stk[0].append(l)
                l, stk = stk
            i = j = j + 1
        elif s[j] in '[(':
            stk = l, stk
            l = []
            i = j = j + 1
        else:
            j += 1 # safe because '[(,)]' are quoted
    if stk: raise ValueError
    if len(l) == 1: l = l[0]
    return l


#####################################################################
#  External downloader process
#####################################################################

def _readlines(fd):
    buf = os.read(fd, 4096)
    if not buf: return None
    # whole lines only, no buffering
    while buf[-1] != '\n':
        buf += os.read(fd, 4096)
    return buf[:-1].split('\n')

import subprocess

class _ExternalDownloader:
    def __init__(self):
        self.popen = subprocess.Popen(
            '/usr/libexec/urlgrabber-ext-down',
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
        )
        self.stdin  = self.popen.stdin.fileno()
        self.stdout = self.popen.stdout.fileno()
        self.running = {}
        self.cnt = 0

    # list of options we pass to downloader
    _options = (
        'url', 'filename',
        'timeout', 'minrate', 'close_connection', 'keepalive',
        'throttle', 'bandwidth', 'range', 'reget',
        'user_agent', 'http_headers', 'ftp_headers',
        'proxy', 'prefix', 'username', 'password',
        'ssl_ca_cert',
        'ssl_cert', 'ssl_cert_type',
        'ssl_key', 'ssl_key_type',
        'ssl_key_pass',
        'ssl_verify_peer', 'ssl_verify_host',
        'size', 'max_header_size', 'ip_resolve',
        'ftp_disable_epsv'
    )

    def start(self, opts):
        arg = []
        for k in self._options:
            v = getattr(opts, k)
            if v is None: continue
            arg.append('%s=%s' % (k, _dumps(v)))
        if opts.progress_obj and opts.multi_progress_obj:
            arg.append('progress_obj=True')
        arg = ' '.join(arg)
        if DEBUG: DEBUG.info('attempt %i/%s: %s', opts.tries, opts.retry, opts.url)

        self.cnt += 1
        self.running[self.cnt] = opts
        os.write(self.stdin, arg +'\n')

    def perform(self):
        ret = []
        lines = _readlines(self.stdout)
        if not lines:
            if DEBUG: DEBUG.info('downloader died')
            raise KeyboardInterrupt
        for line in lines:
            # parse downloader output
            line = line.split(' ', 6)
            _id, size = map(int, line[:2])
            if len(line) == 2:
                self.running[_id]._progress.update(size)
                continue
            # job done
            opts = self.running.pop(_id)
            if line[4] == 'OK':
                ug_err = None
                if DEBUG: DEBUG.info('success')
            else:
                ug_err = URLGrabError(int(line[4]), line[6])
                if line[5] != '0':
                    ug_err.code = int(line[5])
                if DEBUG: DEBUG.info('failure: %s', ug_err)
            _TH.update(opts.url, int(line[2]), float(line[3]), ug_err, opts.async[0])
            ret.append((opts, size, ug_err))
        return ret

    def abort(self):
        self.popen.stdin.close()
        self.popen.stdout.close()
        self.popen.wait()

class _ExternalDownloaderPool:
    def __init__(self):
        self.epoll = select.epoll()
        self.running = {}
        self.cache = {}

    def start(self, opts):
        host = urlparse.urlsplit(opts.url).netloc
        dl = self.cache.pop(host, None)
        if not dl:
            dl = _ExternalDownloader()
            fl = fcntl.fcntl(dl.stdin, fcntl.F_GETFD)
            fcntl.fcntl(dl.stdin, fcntl.F_SETFD, fl | fcntl.FD_CLOEXEC)
        self.epoll.register(dl.stdout, select.EPOLLIN)
        self.running[dl.stdout] = dl
        dl.start(opts)

    def perform(self):
        ret = []
        for fd, event in self.epoll.poll():
            if event & select.EPOLLHUP:
                if DEBUG: DEBUG.info('downloader died')
                raise KeyboardInterrupt
            assert event & select.EPOLLIN
            done = self.running[fd].perform()
            if not done: continue
            assert len(done) == 1
            ret.extend(done)

            # dl finished, move it to the cache
            host = urlparse.urlsplit(done[0][0].url).netloc
            if host in self.cache: self.cache[host].abort()
            self.epoll.unregister(fd)
            self.cache[host] = self.running.pop(fd)
        return ret

    def abort(self):
        for dl in self.running.values():
            self.epoll.unregister(dl.stdout)
            dl.abort()
        for dl in self.cache.values():
            dl.abort()


#####################################################################
#  High level async API
#####################################################################

_async_queue = []

def parallel_wait(meter=None):
    '''Process queued requests in parallel.
    '''

    # calculate total sizes
    meters = {}
    for opts in _async_queue:
        if opts.progress_obj and opts.multi_progress_obj:
            count, total = meters.get(opts.multi_progress_obj) or (0, 0)
            meters[opts.multi_progress_obj] = count + 1, total + opts.size

    # start multi-file meters
    for meter in meters:
        count, total = meters[meter]
        meter.start(count, total)

    dl = _ExternalDownloaderPool()
    host_con = {} # current host connection counts
    single = set() # hosts in single connection mode
    retry_queue = []

    def start(opts, tries):
        opts.tries = tries
        try:
            dl.start(opts)
        except OSError, e:
            # can't spawn downloader, give up immediately
            opts.exception = URLGrabError(5, exception2msg(e))
            _run_callback(opts.failfunc, opts)
            return

        key, limit = opts.async
        host_con[key] = host_con.get(key, 0) + 1
        if opts.progress_obj:
            if opts.multi_progress_obj:
                opts._progress = opts.multi_progress_obj.newMeter()
                opts._progress.start(text=opts.text)
            else:
                opts._progress = time.time() # no updates

    def perform():
        for opts, size, ug_err in dl.perform():
            key, limit = opts.async
            host_con[key] -= 1

            if ug_err is None:
                if opts.checkfunc:
                    try: _run_callback(opts.checkfunc, opts)
                    except URLGrabError, ug_err: pass

            if opts.progress_obj:
                if opts.multi_progress_obj:
                    if ug_err:
                        opts._progress.failure(None)
                    else:
                        opts.multi_progress_obj.re.total += size - opts.size # correct totals
                        opts._progress.end(size)
                    opts.multi_progress_obj.removeMeter(opts._progress)
                else:
                    opts.progress_obj.start(text=opts.text, now=opts._progress)
                    opts.progress_obj.update(size)
                    opts.progress_obj.end(size)
                del opts._progress

            if ug_err is None:
                continue
            if limit != 1 and key not in single and ug_err.errno in (12, 14):
                # One possible cause is connection-limited server.
                # Turn on the max_connections=1 override. BZ 853432
                if DEBUG: DEBUG.info('max_connections(%s) %s => 1', key, limit)
                single.add(key)
                # When using multi-downloader the parent's _curl_cache
                # object is idle. Kill it, as it might use keepalive=1.
                reset_curl_obj()

            retry = opts.retry or 0
            if opts.failure_callback:
                opts.exception = ug_err
                try: _run_callback(opts.failure_callback, opts)
                except URLGrabError, ug_err:
                    retry = 0 # no retries
            if opts.tries < retry and ug_err.errno in opts.retrycodes:
                start(opts, opts.tries + 1) # simple retry
                continue

            if opts.mirror_group:
                mg, errors, failed, removed = opts.mirror_group
                errors.append((opts.url, exception2msg(ug_err)))
                failed[key] = failed.get(key, 0) + 1
                opts.mirror = key
                opts.exception = ug_err
                action = mg.default_action or {}
                if mg.failure_callback:
                    opts.tries = len(errors)
                    action = dict(action) # update only the copy
                    action.update(_run_callback(mg.failure_callback, opts))
                if not action.get('fail', 0):
                    # mask this mirror and retry
                    if action.get('remove', 1):
                        removed.add(key)
                    retry_queue.append(opts)
                    continue
                # fail=1 from callback
                ug_err.errors = errors

            # urlgrab failed
            opts.exception = ug_err
            _run_callback(opts.failfunc, opts)

    try:
        retry_idx = idx = 0
        while True:
            if retry_idx < len(retry_queue):
                # retries first
                opts = retry_queue[retry_idx]
                retry_idx += 1
            elif idx < len(_async_queue):
                # handle next request
                opts = _async_queue[idx]
                idx += 1
            else:
                # both queues are empty
                if not dl.running: break
                perform()
                continue

            # check global limit
            while len(dl.running) >= default_grabber.opts.max_connections:
                perform()
            if DEBUG:
                DEBUG.info('max_connections: %d/%d', len(dl.running), default_grabber.opts.max_connections)

            if opts.mirror_group:
                mg, errors, failed, removed = opts.mirror_group

                # find the best mirror
                best = None
                best_speed = None
                for mirror in mg.mirrors:
                    key = mirror['mirror']
                    if key in removed: continue

                    # estimate mirror speed
                    speed, fail = _TH.estimate(key)
                    speed /= 1 + host_con.get(key, 0)

                    # order by: least failures, private flag, best speed
                    # ignore 'private' flag if there were failures
                    private = not fail and mirror.get('kwargs', {}).get('private', False)
                    speed = -failed.get(key, 0), private, speed
                    if best is None or speed > best_speed:
                        best = mirror
                        best_speed = speed

                if best is None:
                    opts.exception = URLGrabError(256, _('No more mirrors to try.'))
                    opts.exception.errors = errors
                    _run_callback(opts.failfunc, opts)
                    continue

                # update the grabber object, apply mirror kwargs
                grabber = best.get('grabber') or mg.grabber
                opts.delegate = grabber.opts.derive(**best.get('kwargs', {}))

                # update the current mirror and limit
                key = best['mirror']
                limit = best.get('kwargs', {}).get('max_connections')
                opts.async = key, limit

                # update URL and proxy
                url = mg._join_url(key, opts.relative_url)
                url, parts = opts.urlparser.parse(url, opts)
                opts.find_proxy(url, parts[0])
                opts.url = url

            # check host limit, then start
            key, limit = opts.async
            if key in single:
                limit = 1
            while host_con.get(key, 0) >= (limit or 2):
                perform()
            if DEBUG:
                DEBUG.info('max_connections(%s): %d/%s', key, host_con.get(key, 0), limit)

            start(opts, 1)
    except IOError, e:
        if e.errno != 4: raise
        raise KeyboardInterrupt

    finally:
        dl.abort()
        for meter in meters:
            meter.end()
        del _async_queue[:]
        _TH.save()


#####################################################################
#  Host bandwidth estimation
#####################################################################

class _TH:
    hosts = {}
    dirty = None

    @staticmethod
    def load():
        filename = default_grabber.opts.timedhosts
        if filename and _TH.dirty is None:
            try:
                now = int(time.time())
                for line in open(filename):
                    host, speed, fail, ts = line.rsplit(' ', 3)
                    _TH.hosts[host] = int(speed), int(fail), min(int(ts), now)
            except IOError: pass
            _TH.dirty = False

    @staticmethod
    def save():
        filename = default_grabber.opts.timedhosts
        if filename and _TH.dirty is True:
            tmp = '%s.%d' % (filename, os.getpid())
            try:
                f = open(tmp, 'w')
                for host in _TH.hosts:
                    f.write(host + ' %d %d %d\n' % _TH.hosts[host])
                f.close()
                os.rename(tmp, filename)
            except IOError: pass
            _TH.dirty = False

    @staticmethod
    def update(url, dl_size, dl_time, ug_err, baseurl=None):
        # Use hostname from URL.  If it's a file:// URL, use baseurl.
        # If no baseurl, do not update timedhosts.
        host = urlparse.urlsplit(url).netloc.split('@')[-1] or baseurl
        if not host: return

        _TH.load()
        speed, fail, ts = _TH.hosts.get(host) or (0, 0, 0)
        now = time.time()

        if ug_err is None:
            # defer first update if the file was small.  BZ 851178.
            if not ts and dl_size < 1e6: return
            # k1: the older, the less useful
            # k2: <500ms readings are less reliable
            # speeds vary, use 10:1 smoothing
            k1 = 2**((ts - now) / default_grabber.opts.half_life)
            k2 = min(dl_time / .500, 1.0) / 10
            if k2 > 0:
                speed = (k1 * speed + k2 * dl_size / dl_time) / (k1 + k2)
            fail = 0
        elif getattr(ug_err, 'code', None) == 404:
            fail = 0 # alive, at least
        else:
            fail += 1 # seems dead

        _TH.hosts[host] = speed, fail, now
        _TH.dirty = True

    @staticmethod
    def estimate(baseurl):
        _TH.load()

        # Use just the hostname, unless it's a file:// baseurl.
        host = urlparse.urlsplit(baseurl).netloc.split('@')[-1] or baseurl

        default_speed = default_grabber.opts.default_speed
        try: speed, fail, ts = _TH.hosts[host]
        except KeyError: return default_speed, 0

        speed *= 2**-fail
        k = 2**((ts - time.time()) / default_grabber.opts.half_life)
        speed = k * speed + (1 - k) * default_speed
        return speed, fail

#####################################################################
#  TESTING
def _main_test():
    try: url, filename = sys.argv[1:3]
    except ValueError:
        print 'usage:', sys.argv[0], \
              '<url> <filename> [copy_local=0|1] [close_connection=0|1]'
        sys.exit()

    kwargs = {}
    for a in sys.argv[3:]:
        k, v = string.split(a, '=', 1)
        kwargs[k] = int(v)

    set_throttle(1.0)
    set_bandwidth(32 * 1024)
    print "throttle: %s,  throttle bandwidth: %s B/s" % (default_grabber.throttle, 
                                                        default_grabber.bandwidth)

    try: from progress import text_progress_meter
    except ImportError, e: pass
    else: kwargs['progress_obj'] = text_progress_meter()

    try: name = apply(urlgrab, (url, filename), kwargs)
    except URLGrabError, e: print e
    else: print 'LOCAL FILE:', name


def _retry_test():
    try: url, filename = sys.argv[1:3]
    except ValueError:
        print 'usage:', sys.argv[0], \
              '<url> <filename> [copy_local=0|1] [close_connection=0|1]'
        sys.exit()

    kwargs = {}
    for a in sys.argv[3:]:
        k, v = string.split(a, '=', 1)
        kwargs[k] = int(v)

    try: from progress import text_progress_meter
    except ImportError, e: pass
    else: kwargs['progress_obj'] = text_progress_meter()

    def cfunc(filename, hello, there='foo'):
        print hello, there
        import random
        rnum = random.random()
        if rnum < .5:
            print 'forcing retry'
            raise URLGrabError(-1, 'forcing retry')
        if rnum < .75:
            print 'forcing failure'
            raise URLGrabError(-2, 'forcing immediate failure')
        print 'success'
        return
        
    kwargs['checkfunc'] = (cfunc, ('hello',), {'there':'there'})
    try: name = apply(retrygrab, (url, filename), kwargs)
    except URLGrabError, e: print e
    else: print 'LOCAL FILE:', name

def _file_object_test(filename=None):
    import cStringIO
    if filename is None:
        filename = __file__
    print 'using file "%s" for comparisons' % filename
    fo = open(filename)
    s_input = fo.read()
    fo.close()

    for testfunc in [_test_file_object_smallread,
                     _test_file_object_readall,
                     _test_file_object_readline,
                     _test_file_object_readlines]:
        fo_input = cStringIO.StringIO(s_input)
        fo_output = cStringIO.StringIO()
        wrapper = PyCurlFileObject(fo_input, None, 0)
        print 'testing %-30s ' % testfunc.__name__,
        testfunc(wrapper, fo_output)
        s_output = fo_output.getvalue()
        if s_output == s_input: print 'passed'
        else: print 'FAILED'
            
def _test_file_object_smallread(wrapper, fo_output):
    while 1:
        s = wrapper.read(23)
        fo_output.write(s)
        if not s: return

def _test_file_object_readall(wrapper, fo_output):
    s = wrapper.read()
    fo_output.write(s)

def _test_file_object_readline(wrapper, fo_output):
    while 1:
        s = wrapper.readline()
        fo_output.write(s)
        if not s: return

def _test_file_object_readlines(wrapper, fo_output):
    li = wrapper.readlines()
    fo_output.write(string.join(li, ''))

if __name__ == '__main__':
    _main_test()
    _retry_test()
    _file_object_test('test')
