function h5found = hdf5cd(h5info, path, pos)
% node = hdf5cd(h5info, path, [pos=''])
%
% pos should be passed in if you're not starting at the root, e.g.
% pos=h5info.Name (except h5info = '' for the root)
%
% hdf5cd will traverse as far as it can.  It doesn't actually return an
% error currently.

if ~exist('pos', 'var') pos = ''; end

[tok, path] = strtok(path, '/');

if isempty(tok)
    h5found = h5info;
    return
else
    pos = [pos, '/', tok];
    
    for i = 1:length(h5info.Groups)
        if strcmp(pos, h5info.Groups(i).Name)
            h5found = hdf5cd(h5info.Groups(i), path, pos);
            return
        end
    end
    
    for i = 1:length(h5info.Datasets)
        if strcmp(pos, h5info.Datasets(i).Name)
            h5found = h5info.Datasets(i);
            return
        end
    end
end

h5found = [];

return