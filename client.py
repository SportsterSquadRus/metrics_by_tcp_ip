import socket
import time


class ClientError(Exception):
    pass


class Client:
    def __init__(self, host_ip, host_port, timeout=None):
        self.host_ip = host_ip
        self.host_port = host_port
        self.timeout = timeout

    def get(self, metric_name):
        get_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.timeout != None:
            get_sock.settimeout(self.timeout)
        msg_get = 'get {m}\n'.format(m=metric_name)
        while True:
            try:
                get_sock.connect((self.host_ip, self.host_port))
                get_sock.sendall(msg_get.encode())
            except (ConnectionRefusedError, socket.timeout, socket.error):
                raise ClientError
            dic = {}
            try:
                get_data = get_sock.recv(1024)
                if get_data.decode()[0:2] == 'ok' and get_data.decode() != 'ok\n\n':

                    k = get_data.decode().split()
                    
                    for i in range(1, len(k), 3):
                        if k[i] not in dic:
                            dic[k[i]] = [(int(k[i + 2]), float(k[i + 1]))]
                        else:
                            dic[k[i]].append((int(k[i + 2]), float(k[i + 1])))
                    for j in dic:
                        dic[j] = sorted(dic[j])        
                    return dic
                elif get_data.decode() == 'ok\n\n':
                    return dic
                elif get_data.decode() == 'error\n\n':
                    break
            except IndexError:
                raise ClientError

        get_sock.close()

    def put(self, metric_name, digit, timestamp=None):
        if timestamp == None:
            self.timestamp = int(time.time())
        else:
            self.timestamp = timestamp
        put_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.timeout != None:
            put_sock.settimeout(self.timeout)

        msg = 'put {m} {d} {t}\n'.format(
            m=metric_name, t=self.timestamp, d=digit)
        while True:
            try:
                put_sock.connect((self.host_ip, self.host_port))
                put_sock.sendall(msg.encode())
            except (ConnectionRefusedError, socket.timeout, socket.error):
                raise ClientError

            try:
                rcv_data = put_sock.recv(1024)
                if rcv_data.decode() == 'ok\n\n':
                    break
                else:
                    raise ClientError
            except (Exception):
                raise ClientError
        put_sock.close()

# k = Client('127.0.0.1', 9999)
# k.put("palm.cpu", 0.5, timestamp=1150864247)
# k.get('*')