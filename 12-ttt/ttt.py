import sys
import socketserver
import http.server
import urllib.parse
import json


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass


class Game:
    def __init__(self, name):
        self.name = name
        self.id = 0 if not games else max(games, key=int) + 1
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.next = 1
        self.winner = None

        games[self.id] = self

    def play(self, x, y):
        self.board[y][x] = self.next

        for row in self.board:
            if row[0] != 0 and row[0] == row[1] and row[1] == row[2]:
                self.winner = self.next

        for column in [0, 1, 2]:
            if self.board[0][column] != 0 and self.board[0][column] == self.board[1][column] and self.board[1][column] == self.board[2][column]:
                self.winner = self.next

        if self.board[0][0] != 0 and self.board[0][0] == self.board[1][1] and self.board[1][1] == self.board[2][2]:
            self.winner = self.next

        if self.board[0][2] != 0 and self.board[0][2] == self.board[1][1] and self.board[1][1] == self.board[2][0]:
            self.winner = self.next

        if self.winner is None and 0 not in self.board[0] and 0 not in self.board[1] and 0 not in self.board[2]:
            self.winner = 0

        self.next = 2 if self.next == 1 else 1


class GameHandler(http.server.BaseHTTPRequestHandler):
    def send(self, response):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(response), 'utf8'))

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(url.query))
        command = url.path[1:]

        if command == 'start':
            if 'name' in params:
                game = Game(params['name'])
            else:
                game = Game('')
            response = {'id': game.id}
            self.send(response)

        elif command == 'status':
            if 'game' in params and params['game'].isnumeric() and int(params['game']) in games:
                game = games[int(params['game'])]
                response = {}
                if game.winner is not None:
                    response['winner'] = game.winner
                else:
                    response['board'] = game.board
                    response['next'] = game.next
                self.send(response)
            else:
                self.send_error(404)

        elif command == 'play':
            if 'game' in params and params['game'].isnumeric() and int(params['game']) in games:
                response = {}
                game = games[int(params['game'])]

                if game.winner is not None:
                    response['status'] = 'bad'
                    response['message'] = 'game over'

                elif 'player' not in params or not params['player'].isnumeric() or int(params['player']) != game.next:
                    response['status'] = 'bad'
                    response['message'] = 'invalid player'

                elif 'x' not in params or not params['x'].isnumeric() or int(params['x']) not in [0, 1, 2]:
                    response['status'] = 'bad'
                    response['message'] = 'invalid coordinate x'

                elif 'y' not in params or not params['y'].isnumeric() or int(params['y']) not in [0, 1, 2]:
                    response['status'] = 'bad'
                    response['message'] = 'invalid coordinate y'

                elif game.board[int(params['y'])][int(params['x'])] != 0:
                    response['status'] = 'bad'
                    response['message'] = 'field not empty'

                else:
                    game.play(int(params['x']), int(params['y']))
                    response = {'status': 'ok'}

                self.send(response)

            else:
                self.send_error(404)

        elif command == 'list':
            response = []
            for game in games.values():
                response.append({
                    'name': game.name,
                    'id': game.id,
                    'board': game.board})

            self.send(response)

        else:
            self.send_error(404)


port = int(sys.argv[1])
games = {}
server = Server(('', port), GameHandler)
server.serve_forever()
