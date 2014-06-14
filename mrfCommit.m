function mrfCommit(mrfiles)
% mrfCommit
%
% This function should eventually check whether the specified group exists
% in the repository and then do a PUT or a POST as appropriate.  For now,
% this is just doing a PUT no matter what
% It also calls get_repository to update the remote repository.  This could
% certainly be done more efficiently - in an ideal world, the server side
% diff / merge can return a list of operations to perform locally, thus
% avoiding binary network traffic.  The PyTables undo log might be an
% interesting place to look for how to do this super-spiffy.  Or
% alternatively you might want to do it in Java.  Merging with MATLAB might
% be a pain in the butt... 


repository_url = mrFilesGet(mrfiles,'repository');
authstr        = mrFilesGet(mrfiles,'authstr');
fname = mrFilesGet(mrfiles, 'fname');

if notDefined('repository_url'), warndlg('Please set repository URL'); return; end
if notDefined('authstr'),        warndlg('Please set authrstr'); return; end

mode = 'PUT';
[resp, output] = http_transport_file(repository_url, mode, fname, authstr);

% Currently, the system almost always returns a code 200, even when there's a
% problem...
if resp.code ~= 200
    myErrorDlg(['Recieved response code ' resp.message.toCharArray' ...
                ' from ' repository_url ' during ' mode])
else
    msgbox(['Commit ' mrFilesGet(mrfiles, 'fname') ' to ' repository_url ...
            sprintf(':\n') output])

    % Once we're updating and not overwriting, we should then do this:
    % mrfFetch
end

return;
