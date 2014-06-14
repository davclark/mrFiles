function H = struct2hdf5(M, name)
% This function simply takes M, a matlab struct, and saves it into an hdf5
% file.  This differs from the standard matlab mechanism of using an
% hdf5.h5composite type to store all the elements in one dataset. H is an HDF5 object, 
% optionally assigning it the name, 'name' (though saving ignores names...)

elts = fieldnames(M);
% {:} syntax expands the elts into a comma separated argument list
H = hdf5.h5compound(elts{:});
if nargin >= 2
    setName(H, name);
end

for j=1:length(elts)
    curr = M.(elts{j});

    if ischar(curr)
        curr = hdf5.h5string(curr);
    elseif not(isscalar(curr))
        curr = hdf5.h5array(curr);
    end

    setMember(H, elts{j}, curr);
end
