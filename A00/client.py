import socket


class Query:
    """
    Query class
    """

    def __init__(self, q_type, length: int, msg):
        self.q_type = q_type
        self.length = length
        self.msg = msg

    def get_data(self):
        """
        convert all query data into network ready bytes
        :return: bytes of query data
        """
        type_bytes = bytearray(str.encode(self.q_type, "utf-8"))
        length_bytes = bytearray(self.length.to_bytes(1, "big"))
        msg_bytes = bytearray(str.encode(self.msg, "utf-8"))
        return type_bytes + length_bytes + msg_bytes


def main():
    msg = input("Email to ask\n")
    # Create a TCP/IP socket
    sock = socket.create_connection(("127.0.0.1", 3100))
    try:
        # create query from input
        query = Query("Q", len(msg), msg)
        # send query data to server
        sock.sendall(query.get_data())
        while True:
            # read data send by server
            # read query type
            r_type_data = sock.recv(1)
            r_type = r_type_data.decode("utf-8")
            if r_type == "R":
                # read msg length
                msg_length_data = sock.recv(1)
                # decode the msg_length with Big Endian (network byte order)
                msg_length = int.from_bytes(msg_length_data, "big")
                # read the actual msg
                msg_data = sock.recv(msg_length)
                msg = msg_data.decode("utf-8")
                print(
                    f"------------Response------------\n"
                    f"Type: {r_type}\nLength: {msg_length}\nAnswer: {msg}\n"
                    f"--------------------------------"
                )
                break
            else:
                # case of incorrect response
                print("Error in response")
                break
    except Exception as e:
        # print error message
        print(e)
    finally:
        # close socket
        sock.close()


if __name__ == "__main__":
    main()
