function mrfiles = mrfInit(mrfiles, sessionCode, experiment, user)
% mrfiles = mrfInit(mrfiles,  [sessionCode=''], [experiment=''], [user=license.user])
%
% Adds where data is stored and 
% is stored and how to authenticate to it

if ~exist('mrfiles','var')|isempty(mrfiles), error('mrfInit: need mrfiles "object"'); end

% user should NOT be set from the hdf5 file, as multiple users can
% use the same file
if(~exist('user','var')) s=license('inuse'); user=s(1).user; end

% These should be fetched from the hdf5 file, or if not yet defined, from
% the system.
if(~exist('sessionCode','var')) sessionCode = ''; end
if(~exist('experiment','var')) experiment = ''; end
serverURL = 'http://orange.stanford.edu';

prompt   = {'Experiment','Session Code','User', 'Password'};
name     = 'Repository Settings';
numlines = 1;

defaultanswer = {experiment,sessionCode,user, ''};

% Final 'on' allows resizing
answer = inputdlg(prompt,name,numlines,defaultanswer,'on');

if length(answer)
    rURL = sprintf('%s/mrFiles/%s.h5/%s',serverURL,answer{1},answer{2});
    mrfiles = mrFilesSet(mrfiles,'repository',rURL); 

    str = [answer{3} ':' answer{4}];
    encodedStr = org.apache.axis.encoding.Base64.encode(double(str));
    authstr = ['Basic ' encodedStr.toCharArray'];
    mrfiles = mrFilesSet(mrfiles,'authstr', authstr); 
    disp('mrfiles initialized')
end

return;
