function mrfiles = mrFilesSet(mrfiles,param,val)
%mrFilesSet - Set parameters in mrFILES structure
%
%   mrf = mrFilesSet(mrf,param,val)
%
%
% Parameters:
% 'authstr'         - Authentication string
% 'respositoryurl'  - Where the data are stored on the server
%         
% Example
%
%

if notDefined('param'), error('Parameter required'); end

switch lower(param)
    case 'authstr'
        mrfiles.authstr = val;
    case {'respositoryurl','repository'}
        mrfiles.repositoryURL = val;
    case 'path'
        if ~isstr(val)
            error('mrFilesSet: mrfiles path must be a string')
        end
        % this is untested and really not worth doing - but I leave it just
        % in case someone gets a bee in their bonnet
%         if strmatch(val, mrfiles.path)
%             mrfiles.where = hdf5cd(mrfiles.h5i.GroupHierarchy, val);    
%         else
%             offset = length(val)+2; % or +1 here?
%             rest = val(offset:end);
%             mrfiles.where = hdf5cd(mrfiles.where, rest, mrfiles.path);
%         end
        
        mrfiles.path = val;
        % Given the weak coupling between this and what actually happens -
        % we do a refresh every time for now...
        if exist(mrfiles.fname, 'file')
            mrfiles.h5i = hdf5info(mrfiles.fname);
            mrfiles.where = hdf5cd(mrfiles.h5i.GroupHierarchy, val);
        else
            mrfiles.where = [];
            mrfiles.h5i = [];
        end
        % Now we try to find if there's actually anything there
        
    otherwise
        error('Unknown parameter');
end

return;
