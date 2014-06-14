function [mrfiles, pos] = mrfPos(mrfiles, opt, str)
% [mrfiles, pos] = mrfGetPos(mrfiles, opt, [str])
%
% Precondition: should have mrfSetWhere to a location containing numbered
% versions of datasets.  Thus, mrfiles.where is a Group or [] / empty.
%
% str is there for future fine-grained position selection.  As in per-user,
% or other keyword.
%
% provides a variety of options for determining a particular position under
% the current location in mrfiles
%
% This function should only be used on groups containing numbered
% datasets

if ~exist('opt', 'var'), opt = ''; end

% For now we assume that the path where ROIs live will _only_ ever have
% 0, 1, 2 etc. or otherwise nothing.  The worst case would be a group
% ends up in there with a numeric name like '1'.  For now, I put in an
% assertion


if ~isempty(mrFilesGet(mrfiles, 'groups'))
    error('mrfGetPos:Malformed', ...
          ['found group in Dataset location ' mrfiles.where.path]);
end

datasets = mrFilesGet(mrfiles, 'datasets');

pathStr = mrFilesGet(mrfiles, 'path');
offset = length(pathStr)+2;

switch opt
    case 'new'
        if strcmp(mrfiles.writeMode, 'overwrite')
            pos = 0;
        else
            % The convention is that actual ROI coords are stored as 0, 1,
            % 2, ...  These are HDF5 datasets
            pos = 0;
            % Loop is skipped if there are no datasets...
            for i=1:length(datasets)
                n = str2num(datasets{i}(offset:end));
                if pos <= n
                    pos = n + 1;
                end
            end
        end
        
        mrfiles = mrFilesSet(mrfiles, 'path', [pathStr, '/', num2str(pos)]);
            
    case 'max'
        if isempty(datasets)
            error('mrfPos:Malformed', ...
                  ['no Datasets under' pathStr]);
        else
            newPath = datasets{1};
            pos = str2num(newPath(offset:end));
            
            for i=2:length(datasets)
                n = str2num(datasets{i}(offset:end));
                if pos < n
                    pos = n;
                    newPath = datasets{i};
                end
            end
            
            mrfiles = mrFilesSet(mrfiles, 'path', newPath);
        end
    otherwise
        % There could be default options, but for now...
        error('mrfGetPos: unsupported option');    
end