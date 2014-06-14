function mrfiles = mrfSaveHdf5(mrfiles, s, dsetfield)
% mrfSaveHdf5(mrfiles, s, dsetfield, [where])
%
% takes a structure 's' and saves it to file 'h5name' in location 'loc'
% dsetfield determines which field of the struct gets treated as the
% dataset, all remaining fields become metadata

fname = mrFilesGet(mrfiles, 'fname');
loc = mrFilesGet(mrfiles, 'path');

hdf5write(fname, loc, s.(dsetfield), 'WriteMode', mrfiles.writeMode);
mrfiles.writeMode = 'append';

attr_details.AttachedTo = loc;
attr_details.AttachType = 'dataset';

thisVersion = version;
% Note - we are purposefully overwriting this if it's already there!
s.matlab_ver = str2num(thisVersion(1:3));

attr_names = fieldnames(s);
for n = 1:length(attr_names)
    if strcmp(attr_names{n}, dsetfield)
        % Already saved this as the dataset
        continue
    end
    attr_details.Name = attr_names{n};
    % If this isn't 'append' mode, it'd erase everything else
    hdf5write(fname, attr_details, s.(attr_names{n}), ...
              'WriteMode', 'append');
end

% Our info has now changed
mrfiles.h5i = hdf5info(fname);