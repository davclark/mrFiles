# This class should never know anything about network connections, the web, etc.

from tables import openFile, Leaf, Group
import numpy
from time import ctime
 
class local_h5_repos:
    """A class to manage an actual local repository
    I want to guarantee that methods always return properly, but
    this may not be the case with the constructor - specifically
    file open errors will raise"""
    file = None
    where = None
    mode = None
    # undo_mark = None
    externs = None

    def __init__(self, fname, mode='r', path=None):
        self.mode = mode
        self.file = openFile(fname, self.mode) 
        
        # if mode != 'r':
        #     if not self.file.isUndoEnabled():
        #         self.file.enableUndo()
        #     self.undo_mark = self.file.mark()
        if path:
            self.set_where(path)
        else:
            self.where = self.file.root


    def set_where(self, path):
        """Set a kind of working directory in self.where"""
        try:
            self.where = self.file.getNode(path)
        except:
            if self.mode == 'w' or self.mode == 'a':
                (parent, grpnam) = path.rsplit('/', 1)
                if parent:
                    parent = self.set_where(parent)
                else:
                    parent = '/'

                self.where = self.file.createGroup(parent, grpnam)
            else:
                self.where = None
                raise
        
        return self.where

    def put_next(self, object):
        """Put object in numerically next child of current 'where'
        as an Array"""
        curr_max = 0
        for k in self.where._v_children.keys():
            try:
                if int(k) >= curr_max:
                    curr_max = int(k) + 1
            except ValueError:
                pass

        self.file.createArray(self.where, str(curr_max), object, 
                             'external repository')

    def info(self):
        """A list of useful information about the current node, 'where'"""
        # Get all user (i.e. non-PyTables) metadata attributes
        ret_info = {}
        for n in self.where._v_attrs._v_attrnamesuser:
            # Should eventually add something to deal with matlab strings (which
            # end up as matrices)
            if n == 'time':
                ret_info[n] = ctime(self.where._f_getAttr(n))
            else:
                ret_info[n] = self.where._f_getAttr(n)

        if isinstance(self.where, Leaf):
            # Can add extra metadata here or above for both leaves and groups
            ret_info['Number of coords'] = int(self.where.shape[0])
            ret_info['Centroid'] = numpy.mean(self.where).tolist()
            return ('Leaf', ret_info)
        else:
            ret_info['HDF5 group'] = 'contains things'
            return ('Group', ret_info)


    def copy_context(self, dest):
        """copy only user attributes from the current source to a fresh 
        pytables file"""
        # copy_attrs(self.file.root, dest.where)
        pass

    def copy(self, dest, nodes=None):
        """For now, we overwrite anything that might have been there before"""
        # Note - this is an Exception if self.where or dest.where are not groups
        if paths:
            for n in nodes:
                dest.set_where(n.rsplit('/', 1)[0])
                self.copyNode(n, dest.where)
        else:
            self.where._f_copyChildren(dest.where, recursive=True,
                               overwrite=True)
        dest.file.flush()


    def restore(self):
        """resets to undo mark on the pytables file.  Returns True if it did
           anything"""
        # This seems to be more trouble than its worth
        # if self.undo_mark:
        #     self.file.undo(self.undo_mark)
        #     return True
        # else:
        #     return False
        return False


    def close(self):
        self.where = None
        if self.file:
            self.file.close()
        else:
            self.file = None

    
    def extract_path(self, where=None, fields={}): 
        if not self.file:
            return None
        if not where:
            where = self.where

        path_txt = where._v_pathname.split('/')[1:-1]

        for i in range(len(path_txt)):
            # At some point it would be nice to name these properly, but this is
            # not a job for me right now!
            fields.setdefault(str(i), set()).add(path_txt[i])

        return fields


    def subtree_info(self, where=None):
        if not self.file:
            return None
        if not where:
            where = self.where

        if isinstance(where, Leaf):
            return (self.extract_path(where), [where._v_pathname], None)

        fields = {}
        leaves = []
        for node in where._f_walkNodes():
            if isinstance(node, Leaf):
                fields = self.extract_path(node, fields)
                leaves.append(node._v_pathname)

        children = {}
        for (name, node) in where._v_children.items():
            children[name] = node._v_pathname

        return (fields, leaves, children)


    def annotate(self, attrs, where=None):
        """Add the attribute / value pairs in 'attrs' (which should be a mapping
        based on strings) to all leaves under 'where'"""
        if not where:
            where = self.where

        for node in where._f_walkNodes():
            if isinstance(node, Leaf):
                for (k,v) in attrs.items():
                    node.setAttr(k, v)


    def get_values(self, locs):
        """Read the contents at each path specified in locs"""
        return [self.file.getNode(l).read() for l in locs]
