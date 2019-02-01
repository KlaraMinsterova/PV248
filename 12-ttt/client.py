import sys
import urllib.request
import json
import time


def url_to_response(url):
    response = urllib.request.urlopen(url)
    return json.loads(response.read().decode('utf-8'))


def draw_board(current_game):
    for x in range(0, 3):
        line = ''
        for y in range(0, 3):
            played = current_game['board'][x][y]
            if played == 0:
                line += '_'
            elif played == 1:
                line += 'x'
            else:
                line += 'o'
        print(line)


server = 'http://{0}:{1}'.format(sys.argv[1], sys.argv[2])

games = url_to_response('{0}/list'.format(server))
for game in games:
    if (sum(game['board'][0]) + sum(game['board'][1]) + sum(game['board'][2])) == 0:
        print('{0} {1}'.format(game['id'], game['name']))
print("choose game (type id) or start a new game (type 'new' and name): ")

answer = input().strip()
if answer.startswith('new'):
    game_name = answer.replace('new', '').strip()
    new_game = url_to_response('{0}/start?name={1}'.format(server, game_name))
    game_id = new_game['id']
    player = 1
else:
    game_id = answer
    player = 2

over = False
waiting_printed = False

while not over:
    game = url_to_response('{0}/status?game={1}'.format(server, game_id))

    if 'winner' in game:
        if game['winner'] == player:
            print('you win')
        elif game['winner'] == 0:
            print('draw')
        else:
            print('you lose')
        over = True

    elif game['next'] == player:
        draw_board(game)
        invalid_input = True
        while invalid_input:
            print('your turn ({0}): '.format('x' if player == 1 else 'o'))
            coordinates = input().strip().split()
            if len(coordinates) == 2:
                play = url_to_response('{0}/play?game={1}&player={2}&x={3}&y={4}'.format(server, game_id, game['next'], coordinates[0], coordinates[1]))
                if play['status'] == 'ok':
                    invalid_input = False
            if invalid_input:
                print('invalid input')
        waiting_printed = False

    elif not waiting_printed:
        draw_board(game)
        print('waiting for the other player')
        waiting_printed = True
        time.sleep(1)

    else:
        time.sleep(1)
