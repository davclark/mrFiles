# This contains classes and functions for doing useful things with URLs

from re import match

class complete_url:
    base = ''
    args = '' 
    restrictions = []
    parsed_args = {}

    def __init__(self, base=None, args=None):
        if base:
            self.base = base
        if args:
            self.args = args

    def complete(self, rel):
        return self.base+'/'+rel+'?'+self.args

    def add_arg(self, to_add):
        """return the base URL with the arg in to_add"""
        if self.args:
            to_add = self.args+'&'+to_add
        return self.base+'?'+to_add

    def strip_arg(self, to_del):
        """Remove the arg from _all_ future URLs from this instance"""
        arglist = self.args.split('&')
        arglist.remove(to_del)
        self.args = '&'.join(arglist)

    def new_file_loc(self, fname):
        """Replace the filename in the base URL with fname"""
        return self.base.rsplit('/', 1)[0] + '/' + fname

    def hack_complete(self, rel):
        base = self.base.rsplit('.h5')[0]
        return base+'.h5'+rel+'?'+self.args


    def parse_args(self):
        """Split the args into a useful structure"""
        if not(self.restrictions or self.parsed_args):
            args = self.args.split('&')

            if not (len(args) == 1 and args[0] == ''):
                for item in args:
                    (l,r) = item.split('=', 1)
                    m = match('\d+', l)
                    if m:
                        # This is a numeric argument / restriction
                        i = int(m.group())
                        if i >= len(self.restrictions):
                            for j in range(len(self.restrictions), i+1):
                                self.restrictions.append(set())
                            
                        self.restrictions[i].add(r)
                    else:
                        self.parsed_args.setdefault(l, set()).add(r)

        return (self.restrictions, self.parsed_args)
