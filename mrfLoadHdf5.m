function s = mrfLoadHdf5(mrfiles, dsetfield)
% s = mrfLoadHdf5(mrfiles)
% 
% Precondition: Must have done a mrfSetWhere and probably a 'new' mrfPos to set
% this correctly.


if isfield(s, 'matlab_ver')
    thisVersion = version;
    % Note - we are purposefully overwriting this if it's already there!
    running_matlab_ver = str2num(thisVersion(1:3));
    if xor(running_matlab_ver < 7.2, s.matlab_ver < 7.2)
        % In matlab 7.2 and greater, one can add
        % hdf5read(..., 'V71Dimensions', true) to handle files saved w/
        % versions prior to 7.2
        error('mrfLoadHdf5: file saved and loaded with incompatible MATLAB versions');
    end
end

s.(dsetfield) = hdf5read(mrfiles.where);

% Now grab attributes.  For now, there's just color, but it should be
% pretty obvious how to specify more
attr = mrfiles.where.Attributes;
offset = length(mrfiles.where.Name)+2;
for j=1:length(attr)
    stripped_name = attr(j).Name(offset:end);
    switch stripped_name
        case 'color'
            % This is redundant, but an example of how extra processing
            % might be applied to a given attribute (or certain
            % attributes could be excluded).
            s.color = attr(j).Value.Data;
        case {'CLASS', 'FLAVOR', 'VERSION', 'TITLE', 'matlab_ver'}
            % The ALLCAPS are PyTables system data - they should be ignored
            %
            % matlab_ver is handled above, and is not currently returned
        otherwise
            s.(stripped_name) = attr(j).Value.Data;
    end
end

