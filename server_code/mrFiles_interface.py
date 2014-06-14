# This file largely contains code for putting up web pages that allow a user to
# make complex queries against the repository through a web-browser

import os
from mod_python import psp

# Local stuff
from mrFiles_urls import complete_url

# We may eventually want to do some actual numerical stuff in here:
# import numpy

def web_form(req, source, psp_dir, url_helper=None):
    """This provides a simple web-based interface to our data"""
    req.content_type = 'text/html'

    ## Assemble information to be printed
    if not url_helper:
        url_helper = complete_url(req.uri, req.args)

    (curr_type, curr_info) = source.info()
    info = psp.PSP(req, filename=psp_dir+'def_list.psp',
                   vars={'entries': curr_info} )
    
    (fields, leaves, children) = source.subtree_info()

    (restrictions, parsed_args) = url_helper.parse_args() 
    filtered = field_filter(leaves, 
                {'rois': restrictions, 'external': [['external']] } )

    rois = filtered.setdefault('rois', [])
    external = filtered.setdefault('external', [])

    ## Generate the PSP objects
    if children:
        child_links = psp.PSP(req, filename=psp_dir+'named_links.psp',
                              vars={'urls': children.keys(), 
                                    'helper': url_helper})
    else:
        child_links = None

    select_lists = psp.PSP(req, filename=psp_dir+'select_lists.psp', 
                           vars={'choices': fields})
    
    if rois:
        roi_links = psp.PSP(req, filename=psp_dir+'links.psp',
                    vars={'urls': rois, 'helper': url_helper})
    else:
        roi_links = None

    if external: 
        external_links = psp.PSP(req, filename=psp_dir+'links.psp',
                    vars={'urls': source.get_values(external),
                          'helper': None})
    else:
        external_links = None

    top_level = psp.PSP(req, filename=psp_dir+'rois.psp')
    top_level.run({'context': req.uri,
                   'nav_links': child_links,
                   'info': info,
                   'select_lists': select_lists,
                   'roi_links': roi_links,
                   'external_links': external_links,
                   'helper': url_helper})


def new_repo(req, source, psp_dir, url_helper=None):
    """generate a form for creating a new repository file"""
    req.content_type = 'text/html'
    repo_dir = req.filename.rsplit('/', 1)[0]
    files = [f for f in os.listdir(repo_dir) if f[-3:] == '.h5']
    top_level = psp.PSP(req, filename=psp_dir+'new_repo.psp')
    top_level.run({'context': req.uri,
                   'files': files})

def field_filter(paths, fields, catchall='rois'):
    """fields should be a dictionary of a list of sets, only paths (separated
    with '/') with elements matching the appropriate set will be returned.  An
    empty field includes everything"""
    filt_paths = {} 

    for p in paths:
        captured = False
        for (name, filts) in fields.items():
            ps = p.strip('/')
            elts = ps.split('/')
            goes_in = False
            for i in range(len(filts)):
                if len(filts[i]):
                    if len(elts) > i:
                        if elts[i] in filts[i]:
                            goes_in = True
                    else:
                        captured = True
                        break
                    
            if goes_in:
                filt_paths.setdefault(name, []).append(p)
                captured = True

        # If a path was not explicitly captured by a filter rule, and the
        # catchall didn't have any filters, we include it in the catchall
        if not captured and not fields.setdefault(catchall, []):
            filt_paths.setdefault(catchall, []).append(p)

    return filt_paths 
