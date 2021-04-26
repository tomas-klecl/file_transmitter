# either an ip address or a hostname for the server to run on
HOST = '0.0.0.0'
# an integer between 1-65535, values above 1023 are recommended
PORT = 5000
# the absolute path of the directory to save the files in,
# if dot is entered, location of the server.py is used
WORKING_DIRECTORY = r'.'
# max amount of bytes of data to be received at once by the recv method
# an integer >= 1024
BUFFER_SIZE = 4096

# this should not be altered
# a delimiter used to keep client and server data transmission in line
# in case change is necessary, it has to match in both:
# server.py and client.py files
_DELIMITER = "<DELIMITER>"
