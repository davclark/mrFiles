function mrfFetch(mrfiles)
% mrfFetch(mrfiles)
%
% For now I'm just disabling this!
%
% This function gets the remote repository from a specified URL,
% eventually, I want to check whether the local version is current and
% tolerate an unset REPOSITORY_URL and/or AUTHSTR

repository_url = mrFilesGet(mrfiles,'repository');
authstr        = mrFilesGet(mrfiles,'authstr');

if notDefined('repository_url'), warndlg('Please set repository URL'); return; end
if notDefined('authstr'),        warndlg('Please set AUTHRSTR'); return; end

[resp, output] = http_transport_file(repository_url, 'GET', 'repository.h5', authstr);

if resp.code ~= 200
    myErrorDlg(['Recieved response code ' resp.message.toCharArray' ...
                ' from ' repository_url ' during GET'])
else
    msgbox(['Retrieve ' repository_url sprintf(' to repository.h5:\n') output])
end
