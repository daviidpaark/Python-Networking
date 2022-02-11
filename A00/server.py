import socket

# global DB for email -> person
NAME_DB = {
    'rey.sky@gmail.com': 'Rey Skywalker',
    'zhenwu@cs.stonybrook.edu': 'ZhengYu Wu',
    'test1@test.com': 'Test 1'
}


class Response:
    """
    Response class for Query
    """

    def __init__(self, r_type, length, msg):
        self.r_type = r_type
        self.length = length
        self.msg = msg

    def get_data(self):
        """
        convert response data into bytes
        :return: bytes for response content
        """
        type_bytes = bytearray(str.encode(self.r_type, 'utf-8'))
        length_bytes = bytearray(self.length.to_bytes(1, 'big'))
        msg_bytes = bytearray(str.encode(self.msg, 'utf-8'))
        return type_bytes + length_bytes + msg_bytes


def get_name(email: str):
    """
    get person's name by email
    :param email: string of email to lookup
    :return: person's name in string
    """
    return NAME_DB[email]


def main():
    # server address and port that socket binds to
    server_addr = "127.0.0.1"
    server_port = 3100
    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    serversocket.bind((server_addr, server_port))
    # become a server socket
    serversocket.listen()
    # server will constantly check for incoming connection
    while True:
        # accept connections from outside
        clientsocket, address = serversocket.accept()
        print('Connected by ', address)
        # now do something with the clientsocket
        while clientsocket:
            # read data send by client
            # read query type
            q_type_data = clientsocket.recv(1)
            q_type = q_type_data.decode('utf-8')
            if q_type == 'Q':
                # read msg length
                msg_length_data = clientsocket.recv(1)
                # decode the msg_length with Big Endian (network byte order)
                msg_length = int.from_bytes(msg_length_data, 'big')
                # read the actual msg
                msg_data = clientsocket.recv(msg_length)
                msg = msg_data.decode('utf-8')
                # debug print
                print(f'------------Question------------\n'
                      f'Type: {q_type}\nLength: {msg_length}\nQuestion: {msg}\n'
                      f'--------------------------------')
                # get name by email
                # catching email not in DB
                try:
                    name = get_name(msg)
                except KeyError:
                    name = 'Error Name Not Found!'
                # create response objet
                response = Response('R', len(name), name)
                # send response data to client
                clientsocket.sendall(response.get_data())

            else:
                # case of incorrect formatting or EOF for connection close
                clientsocket.sendall(str.encode('Error', 'utf-8'))
                break


if __name__ == '__main__':
    main()
