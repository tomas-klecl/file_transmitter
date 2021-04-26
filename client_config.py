# either the ip address or the hostname of the server to connect to
HOST = "127.0.0.1"
# the port of the server to connect to, an integer between 1-65535
PORT = 5000
# the absolute path of the directory with the FILE_LIST and
# the files for the upload
# if dot is used, location of the client.py is used
WORKING_DIRECTORY = r'.'
# name of the input file with a list of files to send to the server
FILE_LIST = "file_list.txt"
# max amount of bytes of data to send to server at once
# an integer >= 1024
BUFFER_SIZE = 4096

# this should not be altered
# a delimiter used to keep client and server data transmission in line
# in case change is necessary, it has to match in both:
# server.py and client.py files
_DELIMITER = "<DELIMITER>"
