function val = mrFilesGet(mrfiles,param)
%
%   val = mrFilesGet(mrf,param)
%
% Parameters:
% 'authstr'         - Authentication string
% 'respositoryurl'  - Where the data are stored on the server
%         
% Example
%
%

if notDefined('param'), error('Parameter required'); end
val = [];

switch lower(param)
    case 'authstr'
        val = mrfiles.authstr;
    case {'respositoryurl','repository'}
        val = mrfiles.repositoryURL;
    case 'path'
        val = mrfiles.path;
    case 'groups'
        val = {};
        if isfield(mrfiles.where, 'Groups')
            for j = 1:length(mrfiles.where.Groups)
                val{j} = mrfiles.where.Groups(j).Name;
            end
        end
    case 'datasets'
        val = {};
        if isfield(mrfiles.where, 'Datasets')
            for j = 1:length(mrfiles.where.Datasets)
                val{j} = mrfiles.where.Datasets(j).Name;
            end
        end
    case 'fname'
        val = mrfiles.fname;
    otherwise
        error('Unknown parameter');
end

return;

