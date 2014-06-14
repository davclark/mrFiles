function [response, output] = http_transport_file(url_string, mode, fname, auth)
% This function was a testing ground for working out how to manage
% communications between matlab and an http 1.1 server.
%
% INPUTS
% url_string - the literal url string as you would type into a web browser
% mode - 'PUT' 'POST' 'GET' or 'DELETE'
% fname - name of an existing or target local file
%
% OUTPUTS
% response - structure, code = http response number, message = message in a string
% output - response contents if content-type is text/*, confirmation 
%     message otherwise 
% 
% SSL is still entirely unimplemented
%
% Basic functionality was derived from the standard MATLAB urlread.m /
% urlwrite.m 
%
% This function requires Java.

if ~usejava('jvm')
   error('mrFiles:http_transport_file:NoJvm','http_transport_file requires Java.');
end

% According to MathWorks:
% 'This StreamCopier is unsupported and may change at any time.'
% We'll burn that bridge when we come to it
% Presumably, there will be an obvious replacement in urlread/write.m
import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;

% But for now, this is how we copy stuff around:
isc = InterruptibleStreamCopier.getInterruptibleStreamCopier;


% The default ICE http handler is screwey.  I can't figure out how to set
% content-type, and that makes apache angry - it returns a code 406, which
% means it can't find the right mapping for your content type.
% This sun handler works fine.

% NOTE - the following is not terribly robust
if strncmpi('https', url_string, 5)
    j_handler = sun.net.www.protocol.https.Handler;
else
    j_handler = sun.net.www.protocol.http.Handler;
end
    
% Set up the HTTP connection
j_url_obj = java.net.URL([], url_string, j_handler);
j_conn = j_url_obj.openConnection;

% This doesn't prompt for a password, sadly
% j_conn.setAllowUserInteraction(true)


if nargin > 3
    j_conn.setRequestProperty('Authorization', auth);
end

if strcmpi(mode, 'PUT')
    j_in_stream = java.io.FileInputStream(fname);
    http_put_stream(j_conn, j_in_stream)
    j_out_stream = java.io.ByteArrayOutputStream;
elseif strcmpi(mode, 'GET')
    j_conn.setRequestMethod('GET')
    if nargin > 2
        j_out_stream = java.io.FileOutputStream(fname);
    else
        j_out_stream = java.io.ByteArrayOutputStream;
    end
end

response.code = j_conn.getResponseCode;
response.message = j_conn.getResponseMessage;


% Get the server response
% PROBLEM - for now this breaks with error codes ~= 200
j_in_stream = j_conn.getInputStream;
isc.copyStream(j_in_stream,j_out_stream);
j_in_stream.close;

% matches text/plain, text/html, ...
if strncmp(j_conn.getContentType, 'text/', 5)
    if nargin <= 2 || strcmpi(mode, 'PUT')
        % This method of string conversion copied from urlread.m / urlwrite.m
        % it only works on the ByteArray kind of stream (I think)
        output = char(uint8(j_out_stream.toByteArray'));
    else
        output = 'Text file transferred';
    end
else
    output = 'Binary file transferred';
end

j_out_stream.close;

return;
