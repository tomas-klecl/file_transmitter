import socket
import os
import hashlib
from server_config import (HOST, PORT, WORKING_DIRECTORY,
                           BUFFER_SIZE, _DELIMITER)


def check_server_configuration():
    if type(HOST) != str:
        print('Please enter either an ip address or a hostname' +
              ' for the server to run on in the HOST field.')
        exit()
    if ((type(PORT) != int) or (PORT < 1) or (PORT > 65535)):
        print('Please enter an integer value from 1-65535 for the' +
              ' PORT field. Value above 1023 is recommended.')
        exit()
    if ((WORKING_DIRECTORY != '.') and (not os.path.isdir(WORKING_DIRECTORY))):
        print(f'Working directory {WORKING_DIRECTORY} has not been found.' +
              ' Use either \'.\' or a valid absolute path.')
        exit()
    if ((type(BUFFER_SIZE) != int) or (BUFFER_SIZE < 1024)):
        print('Please enter an integer value >= 1024 for' +
              ' the BUFFER_SIZE field.')
        exit()


def start_a_server():
    with socket.socket() as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Listening as {HOST}:{PORT}")
        client_socket, address = s.accept()
        print(f"[+] {address} has connected.")
        return client_socket


def receive_files(client_socket):
    # receiving file info
    received_data = client_socket.recv(BUFFER_SIZE)
    delimiter_pos = received_data.find(_DELIMITER.encode())
    file_count = int(received_data[:delimiter_pos].decode())
    received_data = received_data[delimiter_pos+len(_DELIMITER):]
    file_list_final = []  # collects names of the files saved by the server
    for n in range(file_count):
        received_data += client_socket.recv(BUFFER_SIZE)
        delimiter_pos = received_data.find(_DELIMITER.encode())
        file_name_ext = received_data[:delimiter_pos].decode()
        file_name = os.path.splitext(os.path.basename(file_name_ext))[0]  # removes absolute path if it is there
        file_ext = os.path.splitext(file_name_ext)[1]
        received_data = received_data[delimiter_pos+len(_DELIMITER):]

        # renaming received files that already exist in the working directory
        file_copy_num = 1
        while True:
            file_exists = os.path.isfile(f"{WORKING_DIRECTORY}/{file_name}{file_ext}")
            if file_exists:
                file_ext = os.path.splitext(file_name_ext)[1]  # reset to keep the '(file_copy_num).ext' format in the next line in case of multiple copies
                file_ext = f'({file_copy_num}){file_ext}'
                file_copy_num += 1
            else:
                file_list_final.append(f'{file_name}{file_ext}')
                break

        # writing received file from the client
        with open(f"{WORKING_DIRECTORY}/{file_name}{file_ext}", "wb") as f:
            while True:
                if _DELIMITER.encode() in received_data:  # end of file has been received
                    delimiter_pos = received_data.find(_DELIMITER.encode())
                    f.write(received_data[:delimiter_pos])
                    print(f'{file_name}{file_ext} has been uploaded.')
                    received_data = received_data[delimiter_pos+len(_DELIMITER):]
                    break
                f.write(received_data)
                received_data = client_socket.recv(BUFFER_SIZE)

    # checking file integrity
    for new_file in file_list_final:
        with open(f"{WORKING_DIRECTORY}/{new_file}", "rb") as f:
            bytes_content = f.read()
            sha3_server = hashlib.sha3_512(bytes_content).hexdigest()
            received_data += client_socket.recv(BUFFER_SIZE)
            delimiter_pos = received_data.find(_DELIMITER.encode())
            sha3_client = received_data[:delimiter_pos]
            received_data = received_data[delimiter_pos+len(_DELIMITER):]
            if sha3_server.encode() == sha3_client:
                print(f'Integrity of {new_file} has been' +
                      ' successfully verified.')
            else:
                print(f'{new_file} sent by the client is not matching the' +
                      ' one saved by the server. Find what modified the data.')


if __name__ == '__main__':
    check_server_configuration()
    receive_files(start_a_server())
