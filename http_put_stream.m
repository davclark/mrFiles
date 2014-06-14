function http_put_stream(j_conn, j_in_stream)
% http_put_stream(j_conn, j_in_stream)
%
% INPUTS
% j_conn - an HttpURLConnection
% j_in_stream - will be sent as the PUT request body using an
% (unsupported) InterruptibleStreamCopier
%
% This function requires Java.

if ~usejava('jvm')
   error('mrFiles:http_put_stream:NoJvm','http_put_stream requires Java.');
end

% According to MathWorks:
% 'This StreamCopier is unsupported and may change at any time.'
% We'll burn that bridge when we come to it
import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;

% But for now, this is how we copy stuff around:
isc = InterruptibleStreamCopier.getInterruptibleStreamCopier;

j_conn.setRequestMethod('PUT')
j_conn.setDoOutput(true)
% this is what we're calling hdf5 files these days - we may want to make
% this more flexible
j_conn.setRequestProperty('Content-Type', 'application/octet-stream')

% Print the file we want to print
out_stream = j_conn.getOutputStream;
isc.copyStream(j_in_stream, out_stream)
j_in_stream.close
out_stream.close % this isn't strictly necessary - it's a no-op