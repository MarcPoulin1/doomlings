import socket
from _thread import *
import pickle
from game import Game
import json
import traceback

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = socket.gethostbyname(socket.gethostname())
port = 5050

global num_players
num_players = 2

try:
    s.bind((server, port))
except socket.error as e:
    print(e)

s.listen(num_players)
print('Waiting for connections.')

global active_players
active_players = 0
game = Game(num_players)


def threaded_client(conn, game, player_id):
    global active_players
    global num_players

    if player_id == num_players:
        conn.close()
        print(f'Player {player_id} was disconnected from the server because the maximum number of players 2 was '
              f'already reached.')

        active_players -= 1

        print(f'Number of players: {active_players}')

    else:
        conn_info = str.encode(str(player_id))
        conn.send(conn_info)

        while True:
            try:
                data = conn.recv(4096*8).decode()
                if not data:
                    break
                if data == 'get':
                    conn.sendall(pickle.dumps(game))

                elif data == 'connected?':
                    pass

                else:
                    data_dict = json.loads(data)
                    if 'function' in data_dict:
                        print(f'Received data: {data_dict}')
                        function = data_dict['function']
                        params = data_dict['params']
                        game_function = getattr(game, function)
                        game_function(**params)
                        conn.sendall(pickle.dumps(game))
            except Exception as e:
                print(traceback.format_exc())
                break

        print(f'Player {player_id} disconnected.')

        active_players -= 1

        print(f'Number of players: {active_players}')

        conn.close()


while True:
    conn, address = s.accept()
    print(f'{address} connected to the server.')

    start_new_thread(threaded_client, (conn, game, active_players))
    active_players += 1
    print(f'Number of players: {active_players}')




