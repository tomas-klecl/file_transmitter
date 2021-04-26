import socket
import os
import re
import hashlib
from client_config import (HOST, PORT, WORKING_DIRECTORY, FILE_LIST,
                           BUFFER_SIZE, _DELIMITER)


def check_client_configuration():
    if type(HOST) != str:
        print('Please enter either the ip address or the hostname' +
              ' of the server you are connecting to in the HOST field.')
        exit()
    if ((type(PORT) != int) or (PORT < 1) or (PORT > 65535)):
        print('Please enter an integer value between 1-65535 of the server' +
              ' you are connecting to in the PORT field.')
        exit()
    if ((WORKING_DIRECTORY != '.') and (not os.path.isdir(WORKING_DIRECTORY))):
        print(f'Working directory {WORKING_DIRECTORY} has not been found.' +
              ' Use either \'.\' or a valid absolute path.')
        exit()
    if not os.path.isfile(f'{WORKING_DIRECTORY}/{FILE_LIST}'):
        print(f'FILE_LIST {FILE_LIST} has not been found in the working' +
              ' directory. Check for spelling errors and whether it\'s' +
              ' really there.')
        exit()
    if ((type(BUFFER_SIZE) != int) or (BUFFER_SIZE < 1024)):
        print('Please enter an integer value >= 1024 for' +
              ' the BUFFER_SIZE field.')
        exit()


def get_file_list():
    with open(f"{WORKING_DIRECTORY}/{FILE_LIST}", "r", encoding="utf-8") as f_list:
        file_list = []
        while True:
            file_line = f_list.readline()
            if file_line == "":  # end of file list
                file_count = len(file_list)
                return file_list, file_count
            else:
                match = re.search("(.*[^\n\r]$)", file_line)  # everything preceding a newline
                try:
                    file_name = match.group(0)
                    if os.path.isfile(f"{WORKING_DIRECTORY}/{file_name}"):
                        print(f'File {file_name} is ready for sending.')
                        file_list.append(file_name)
                    else:
                        print(f'File {file_name} has not been foud and' +
                              ' will not be sent as a result. Please' +
                              ' check if it really exists.')
                except AttributeError:
                    continue  # for lines containing only a newline


def send_files(file_list, file_count):
    with socket.socket() as s:
        print(f"[+] Connecting to {HOST}:{PORT}")
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            print('Connection unsuccessful. Check the values in HOST' +
                  ' and PORT and whether the target server is running.')
            exit()
        print("[+] Connected.")

        # sending file info
        s.send(f'{str(file_count)}{_DELIMITER}'.encode())
        for file_name in file_list:
            s.send(f'{file_name}{_DELIMITER}'.encode())

            # uploading a file
            with open(f'{WORKING_DIRECTORY}/{file_name}', "rb") as f:
                file_size = os.path.getsize(f"{WORKING_DIRECTORY}/{file_name}")
                bytes_transmitted = 0
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:  # file transmission is completed
                        s.send(_DELIMITER.encode())
                        print(f'{file_name} upload finished.')
                        break
                    s.sendall(bytes_read)
                    # transmission completion status
                    bytes_transmitted += BUFFER_SIZE
                    percentage_transmitted = round(bytes_transmitted/file_size * 100, 2)
                    if percentage_transmitted > 100:  # BUFFER_SIZE bigger than file_size
                        print(f'Uploading {file_name}: 100%')
                    else:
                        print(f'Uploading {file_name}:' +
                              f' {percentage_transmitted}%')

        # checking file integrity
        for file_name in file_list:
            with open(f'{WORKING_DIRECTORY}/{file_name}', "rb") as f:
                bytes_content = f.read()
                sha3_content = hashlib.sha3_512(bytes_content).hexdigest()
                s.send(f'{sha3_content}{_DELIMITER}'.encode())


if __name__ == '__main__':
    check_client_configuration()
    file_list, file_count = get_file_list()
    send_files(file_list, file_count)
