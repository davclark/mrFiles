function mrfiles = mrFilesCreate(fname)
% mrFilesCreate(fname)
%
% Holds information about the repository URL and the authentication string.


thisVersion = version;
val = str2num(thisVersion(1:3));
if val < 7.2
    disp('ROIs saved using Matlab < 7.2 are incompatible with Matlab >= 7.2')
end

mrfiles.fname = fname;

if exist(fname, 'file')
    mrfiles.writeMode = 'append';
    
    % Open up the root of the hierarchy and start us there
    mrfiles.h5i = hdf5info(fname);
    mrfiles.where = mrfiles.h5i.GroupHierarchy;
    mrfiles.path = '';
else
    mrfiles.writeMode = 'overwrite';
    
    mrfiles.h5i = [];
    mrfiles.where = [];
    mrfiles.path = '';
end

mrfiles.repositoryURL = [];
mrfiles.authstr = [];

return;
