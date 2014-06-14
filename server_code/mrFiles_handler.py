# Copyright 2006, held by Stanford University
# Written by Dav Clark, davclark@white.stanford.edu

# This file contains the top-level handler function called by mod_python
# It should handle bare-bones transport over HTTP.  Complex web forms should be
# handled by mrFiles_interface.  Dealing with contents of hdf5 files should be
# done with mrFiles_file.

# Standard Lib
import os
import traceback

# Other standard stuff
from mod_python import apache

# Local stuff
from mrFiles_file import local_h5_repos
from mrFiles_interface import web_form, new_repo
from mrFiles_urls import complete_url

# Could set up mappings to things we might find which aren't valid python tokens
# e.g. trMap = {'minc20': 'minc-2.0'}

def handler(req):
    """This sets up common things - like the place I'm going to stick data.
    Then it hands off to a method-specific function."""
    repo = repository(req)

    if req.method == "GET":
        return repo.get()
    elif req.method == "PUT":
        return repo.put()
    elif req.method == "POST":
        return repo.post()
    # elif req.method == "DELETE":
    #     return repo.delete()
    # firefox and maybe other browsers send a HEAD request before doing a "save
    # link as" operation.  Why?  No idea.  But this deals with it.
    elif req.method == 'HEAD':
        return apache.OK
    else:
        # This tells apache to return it's own error page
        return apache.HTTP_NOT_ACCEPTABLE


class repository:
    """A class to keep track of and answer http requests"""
    # Generally, printing of messages should be done with the add_message
    # method, which will print out all messages as text/plain at the end.  Be
    # sure not to do this if you are returning a file!

    # At the end of processing, there should always be a call to the clean_up
    # method.

    # For now we almost always return an apache.OK code, as I've not been able
    # to set up the Matlab / Java client to handle anything else (any other
    # code raises an exception)"""

    # I was going to try to develop a system for appending or removing trailing
    # slashes - but now I have adopted a system of fully ignoring trailing
    # slashes.  Since pages are constructed dynamically, it is straightforward
    # to do fully-qualified links.

    source = None
    dest = None
    # Don't write to this directly!  use self.add_message()
    message = ''
    tempfile = False
    base_dir = '/Library/WebServer/Documents//mrFiles/'
    
    def __init__(self, req, base_dir=None):
        self.req = req
        if type(base_dir) == str:
            self.base_dir = base_dir 
        self.working_file = req.filename
        if self.req.path_info:
                self.req.path_info = self.req.path_info.rstrip('/')


    ## GET functions
    def get(self):
        """download an h5 file, or part of one as a new h5 file, or just get
           info"""
        try:
            if self.req.args == None: # Plain ol' GET
                self.get_file()
            else: # URL contains at least a question mark
                self.get_info()
        except:
            self.handle_exc()
        else:
            self.clean_up()

        return apache.OK


    def get_file(self):
        if self.req.path_info:
            # Create a temp h5 file
            self.dest = local_h5_repos(self.repos_tempnam(), 'w')
            # Set up our local source
            self.source = \
                local_h5_repos(self.req.filename, path=self.req.path_info)
            self.source.copy(self.dest)
            self.source.copy_context(self.dest)

        self.req.content_type = 'application/octet-stream'
        # Returns either a whole local file, or the temp file
        self.req.sendfile(self.working_file)


    def get_info(self):
        """This function handles anything involving more than a straight
        (sub)tree fetch.  As such, it is probably poorly named"""
        self.source = local_h5_repos(self.req.filename, path=self.req.path_info)

        url_helper = complete_url(self.req.uri, self.req.args)
        (restrictions, parsed_args) = url_helper.parse_args()

        if parsed_args.has_key('child'):
            # Create a new sub-repository
            # THIS IS NOT THE RIGHT WAY!
            self.dest = local_h5_repos(self.repos_tempnam(), 'w')
            self.source.copy_context(self.dest)

            self.req.content_type = 'application/octet-stream'
            self.req.sendfile(self.working_file)
        elif parsed_args.has_key('export'):
            # TODO: This is currently redundant with stuff in mrFiles interface
            (fields, leaves, children) = source.subtree_info()   
            filtered = field_filter(leaves, {'rois': restrictions})
            rois = filtered.setdefault('rois', [])

            # TODO: This is currently redundant with stuff in get_file above
            # Create a temp h5 file
            self.dest = local_h5_repos(self.repos_tempnam(), 'w')
            # Set up our local source
            self.source = \
                local_h5_repos(self.req.filename, path=self.req.path_info)
            self.source.copy(self.dest, rois)
            self.source.copy_context(self.dest)

            self.req.content_type = 'application/octet-stream'
            # Returns either a whole local file, or the temp file
            self.req.sendfile(self.working_file)
        elif parsed_args.has_key('external'):
            new_repo(self.req, self.source, self.base_dir+'/code/')
        else:
            web_form(self.req, self.source, self.base_dir+'/code/', url_helper)


    ## PUT functions
    def put(self):
        """Upload an HDF5 file to the repository, or a new subgroup therein"""
        if self.req.path_info:
            self.repos_tempnam()
        elif os.path.exists(self.working_file):
            self.add_message('Did not overwrite ' + self.working_file)
            return apache.OK

        # Upload the file from the client
        try:
            new_fh = open(self.working_file, 'w')
            new_fh.write(self.req.read())
            new_fh.close()

            # This is the file we downloaded
            self.source = local_h5_repos(self.working_file, 'a')
            # this function populates self.req.user
            self.req.get_basic_auth_pw()
            # Note - time is stored in unix format here.  Can use time.ctime to
            # convert it to a reasonable string, and still use numerical
            # comparisons for internal operations
            self.source.annotate({'user': self.req.user,
                                  'time': self.req.request_time})
    
            # Merge into another file if we have a sub-path
            if self.req.path_info:
                self.put_subtree()

            self.add_message('Wrote uploaded data to ' + \
                             self.req.filename + self.req.path_info)
        except:
            self.handle_exc()
        else:
            self.clean_up()

        return apache.OK


    def put_subtree(self):
        # This will be created if it's not there already
        self.dest = local_h5_repos(self.req.filename, 'a', self.req.path_info)
        self.source.copy(self.dest)


    ## POST
    def post(self):
        """Handle interactions with the repository that have side-effects
        apart from DELETEs and PUTs, which are fairly monolithic"""
        try:
            if self.req.args == None: # Plain ol' GET
                raise "unhandled POST operation"
            else: # URL contains at least a question mark
                url_helper = complete_url(self.req.uri, self.req.args)
                (restrictions, parsed_args) = url_helper.parse_args()
                if parsed_args.has_key('external'):
                    if 'create' in parsed_args['external']:
                        self.post_create_external(url_helper) 
        except:
            self.handle_exc()
        else:
            self.clean_up()

        return apache.OK


    def post_create_external(self, url_helper=None):
        """Create a new .h5 repository, and list it as an external repository
        in the current repository"""
        # Here the abstraction of source and destination breaks down a bit.  So,
        # if this seems arbitrary, that's probably because it is.
        self.source = local_h5_repos(self.req.filename, 'r+')
        self.source.set_where('/external')

        post_args = {}
        for line in self.req.readlines():
            (k,v) = line.split('=')
            post_args[k] = v

        try:
            self.source.put_next('http://' + self.req.hostname + 
                                url_helper.new_file_loc(post_args['filename']))
        except:
            self.add_message('trouble using put_next in context (index) repository')
            raise

        new_repo = self.req.filename.rsplit('/', 1)[0] + \
                        '/' + post_args['filename']
        if os.path.isfile(new_repo):
            self.add_message(new_repo + ' already exists!')
            raise IOError

        self.dest = local_h5_repos(new_repo, 'w')
        url_helper.strip_arg('external=create')
        web_form(self.req, self.source, self.base_dir+'/code/', url_helper)


    ## General functions
    def add_message(self, txt):
        """Currently pretty simple-minded, but this could be expanded to allow
           for XML, text, HDF5 or whatever return formats you wanted.

           YOU CAN'T USE THIS AND RETURN A FILE!"""
        self.message += txt + '\n'

    
    def clear_message(self, txt):
        """If you added messages and end up sending a file, you need to avoid
           printing them at clean_up (you can do anything else with them)."""
        self.message = ''

    def repos_tempnam(self):
        self.working_file = os.tempnam(self.base_dir + '/tmp')
        self.tempfile = True
        return self.working_file


    def handle_exc(self):
        """For now, just prints text, but could eventually be smarter"""
        # for now, the Java / MATLAB client can't handle http errors...
        # self.req.status = apache.HTTP_INTERNAL_SERVER_ERROR
        # should probably req.log_error as well...
        traceback.print_exc(file=self.req)
        if self.source:
            if self.source.restore():
                self.add_message('Caught exception on "source" file')    
        if self.dest:
            if self.dest.restore():
                self.add_message('Undid changes to "dest" file')

        self.clean_up()

    def clean_up(self):
        # also clean up - actually could call a clean up function...
        if self.message:
            self.req.content_type = 'text/plain'
            print >>self.req, self.message

        # Before we delete anything - make sure we send it!
        self.req.flush()

        if self.source:
            self.source.close()
        if self.dest:
            self.dest.close()
        if self.tempfile:
            os.remove(self.working_file)
