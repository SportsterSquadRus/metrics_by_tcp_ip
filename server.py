import socket
import select


def run_server(host, port):
    with socket.socket() as sock:
        monitor = []
        dic = {}
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(socket.SOMAXCONN)
        # sock.settimeout(1)
        monitor.append(sock)
        loop(sock, monitor, dic)

def loop(sock, monitor, dic):
    while True:
        try:
            to_read, _, _ = select.select(monitor, [], [])
            for soc in to_read:
                if soc is sock:
                    accept_con(sock, monitor, dic)
                else:
                    process_request(soc, dic)
        except ValueError:
            monitor = [sock]


def accept_con(sock, monitor, dic):
    conn, _ = sock.accept()
    # conn.settimeout(1)
    monitor.append(conn)

def process_request(conn, dic):
    try:
        data = conn.recv(1024)
        if not data:
            conn.close()
        else:
            face_control(conn, data.decode(), dic)
    except socket.error:
        conn.close()

def face_control(conn, data, dic):
    command = ['put', 'get']
    str_splited = data.split()
    # print(str_splited[0])
    if len(data) < 6 or data[-1] != '\n' or str_splited[0] not in command:
        conn.sendall('error\nwrong command\n\n'.encode())
        # conn.close()
    elif data == 'get *\n' and dic == {}:
        conn.sendall('ok\n\n'.encode())
    elif str_splited[0] == 'put':
        if len(str_splited) != 4:
            conn.sendall('error\nwrong command\n\n'.encode())
            # conn.close()
        else:
            try:
                str_splited[3], str_splited[2] = int(
                    str_splited[3]), float(str_splited[2])
            except ValueError:
                conn.sendall('error\nwrong command\n\n'.encode())
            else:
                conn.sendall('ok\n\n'.encode())
                put(str_splited[1:], dic)
            # conn.close()

    elif str_splited[0] == 'get':
        if len(str_splited) != 2:
            conn.sendall('error\nwrong command\n\n'.encode())
            # conn.close()
        else:
            get(str_splited, conn, dic)


def get(str_splited, conn, dic):
    s = 'ok'
    if str_splited[1] == '*':
        for i in dic:
            for j in dic[i]:
                s += '\n' + ' '.join(map(str, j))
    elif str_splited[1] not in dic:
        s += '\n\n'
    elif str_splited[1] in dic:
        for j in dic[str_splited[1]]:
            s += '\n' + ' '.join(map(str, j))
    conn.sendall((s + '\n\n').encode())
    # conn.close()

def put(str_splited, dic):
    if str_splited[0] not in dic:
        dic[str_splited[0]] = [
            (str_splited[0], str_splited[1], str_splited[2])]
    else:
        for i in dic[str_splited[0]]:
            if i[2] == str_splited[2]:
                dic[str_splited[0]].remove(i)
        dic[str_splited[0]].append(
            (str_splited[0], str_splited[1], str_splited[2]))


if __name__ == "__main__":
    run_server("127.0.0.1", 8888)