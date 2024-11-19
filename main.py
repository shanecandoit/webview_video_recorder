from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import threading
import webview
import os
import datetime


def time_clean():
    # time_clean 20241119_154236_966624
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')


class CustomHandler(SimpleHTTPRequestHandler):
    """ Handler for the server """
    def do_POST(self):
        """ Uploads a file to the server """
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # Check if the data is a WebM video file
        # Matroska media container, including WebM
        # 1A 45 DF A3
        start = post_data[:200]
        video_header = b'Content-Type: video/webm; codecs="vp9,opus"\r\n\r\n'  # keep \x1aE\xdf\xa3'
        is_webm = video_header in start
        if is_webm:
            file_extension = 'webm'
            # print('Detected WebM file with size: ' + str(content_length) + ' bytes')

            filename_pattern_prefix = b'Content-Disposition: form-data; name="file"; filename="'
            filename_pattern_postfix = b'.webm"\r\n'
            upload_file_name = None
            if filename_pattern_prefix in post_data:
                upload_file_name = post_data.split(filename_pattern_prefix)[1].split(filename_pattern_postfix)[0]
                upload_file_name = upload_file_name.decode('utf-8')

            video_data_index = start.find(video_header) + len(video_header)
            video_data = post_data[video_data_index:]
            file_size = len(video_data)
            filename = upload_file_name +'_'+ time_clean() + '.' + file_extension

            # if there is a "vids" folder, use it
            if os.path.isdir('vids'):
                filename = 'vids/' + filename

            # save it
            with open(filename, 'wb') as f:
                f.write(video_data)
            print('Saved as output.' + file_extension)
            response = {
                'message': 'Video received',
                'file_size': file_size,
                'file_extension': file_extension
            }

            # tell client the filename
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        response = {
            'message': 'Data received',
            'data': post_data.decode('utf-8')
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))


# create a server
def start_server():
    # Define server address and port
    server_address = ('', 8000)
    # Create HTTP server
    httpd = HTTPServer(server_address, CustomHandler)
    print("Starting server on port 8000...")
    # Start the server
    httpd.serve_forever()

# Start the server in a new thread
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# create a webview
webview.create_window('Recorder', 'http://localhost:8000', 
                      width=800, height=800,
                      )
debug = True
webview.start(debug=debug)

