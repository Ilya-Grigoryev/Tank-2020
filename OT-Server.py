import socket
import threading


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# server.bind(("195.133.48.113", 4444))
server.bind(("localhost", 4444))
server.listen()
print("Server is listening")

global queue, games
queue = []
games = []


def listen_user(user):
    global queue, games
    print("Listening players...")
    data = user.recv(255)
    msg = data.decode('utf-8')
    if "nick" in msg:
        nick = msg.split("nick")[1]
    else:
        nick = 'noname'

    print('New thread!')

    if not((user, nick) in queue) and sum(list(map(lambda game: game[0][0] == user or game[1][0] == user, games))) == 0:
        queue.append((user, nick))
        
    while True:
        for i, u in enumerate(queue):
            try:
                u[0].send('.'.encode('utf-8'))
            except:
                queue.pop(i)

        while len(queue) >= 2:
            try:
                print('Open new game!')
                if queue[0][0] == queue[1][0]:
                    queue.pop(0)
                    continue

                games.append([queue[0], queue[1], 0, 0])
                queue[0][0].send(f'opponent connected :{queue[1][1]}:'.encode('utf-8'))
                queue[1][0].send(f'opponent connected :{queue[0][1]}:'.encode('utf-8'))
                queue = queue[2:]
            except:
                continue

        try:
            data = user.recv(255)
        except OSError:
            return

        msg = data.decode('utf-8')

        for i, (u1, u2, u1_kills, u2_kills) in enumerate(games):
            if u1[0] == user:
                try:
                    if "kill" in msg:
                        games[i][3] += 1
                        if games[i][3] - games[i][2] == 3 or games[i][3] == 5:
                            u1[0].send(f'.LOSE{games[i][2]}:{games[i][3]}LOSE.'.encode('utf-8'))
                            u2[0].send(f'.WIN{games[i][3]}:{games[i][2]}WIN.'.encode('utf-8'))
                    u2[0].send(data)
                except:
                    games.pop(i)
                    user.send('opponent disconnected'.encode('utf-8'))
                    return
                break
            elif u2[0] == user:
                try:
                    if "kill" in msg:
                        games[i][2] += 1
                        if games[i][2] - games[i][3] == 3 or games[i][2] == 5:
                            u1[0].send(f'.WIN{games[i][2]}:{games[i][3]}WIN.'.encode('utf-8'))
                            u2[0].send(f'.LOSE{games[i][3]}:{games[i][2]}LOSE.'.encode('utf-8'))
                    u1[0].send(data)
                except:
                    games.pop(i)
                    user.send('opponent disconnected'.encode('utf-8'))
                    return
                break


def start_server():
    global queue
    while True:
        user_socket, address = server.accept()
        print(f"User <{address[0]}> connected!")

        listen_accepted_user = threading.Thread(target=listen_user, args=(user_socket,))
        listen_accepted_user.start()


if __name__ == '__main__':
    start_server()
