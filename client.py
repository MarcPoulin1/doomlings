from network import Network
import sys
import json
from utils.game_objects import *

name = input('Enter your player name:')

pygame.font.init()

window_width = 700
window_height = 700

game_window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE, depth=64)

buttons = [Button('View Hand', 50, 50, (255, 255, 255), 10, 10, 10),
           Button('View Trait Piles', 150, 50, (255, 255, 255), 10, 10, 10),
           Button('View Game Piles', 250, 50, (255, 255, 255), 10, 10, 10),
           Button('View Game State', 350, 50, (255, 255, 255), 10, 10, 10),
           Button('Play Card', 250, 100, (255, 255, 255), 10, 10, 10, 'conditional'),
           Button('Discard', 350, 100, (255, 255, 255), 10, 10, 10, 'conditional'),
           Button('Random Discard', 350, 100, (255, 255, 255), 10, 10, 10, 'conditional'),
           Button('Stabilize', 450, 100, (255, 255, 255), 10, 10, 10, 'conditional'),
           Button('End Turn', 550, 100, (255, 255, 255), 10, 10, 10, 'conditional')]

view_buttons = [ViewButton('left', 50, 125, (255, 255, 255), active=False),
                ViewButton('right', 70, 125, (255, 255, 255), active=False)]


def redraw_window(win, game, player_id, view_mode):
    win.fill((0, 0, 0))

    if game.game_state[player_id] == 'Waiting for players':
        Button(f'Waiting for all players to connect: {game.connected_players}/{game.num_players}',
               100, 100, (255, 255, 255), 20, 20, 20).draw(win)
    if game.game_state[player_id] == 'End game':

        for button in buttons:
            if not button.active_type == 'conditional':
                button.draw(win)

        if view_mode == 'View Hand':
            view_id = game.players[player_id].view_modes[view_mode]
            if view_id == 0:
                view_buttons[0].active = False
            else:
                view_buttons[0].active = True
            if view_id == game.num_players - 1:
                view_buttons[1].active = False
            else:
                view_buttons[1].active = True
            for button in view_buttons:
                if button.active:
                    button.draw(win)

            font = pygame.font.SysFont('comicsans', 20)
            rendered_text = font.render(game.players[view_id].name, 1, (255, 255, 255))
            win.blit(rendered_text, (125, 150 - rendered_text.get_height() / 2))

            if view_id == player_id:
                hand = Hand(game.players[view_id].hand, win_width=game_window.get_width(),
                            win_height=game_window.get_height())
            else:
                hand = Hand(game.players[view_id].hand, win_width=game_window.get_width(),
                            win_height=game_window.get_height(), view_cards=False)
            hand.draw_hand(win)

            gene_pool = GenePool(game.players[player_id].gene_pool)
            gene_pool.draw_gene_pool(win)

            selected_cards = [selected_card for selected_card in game.players[player_id].current_selection['View Hand']
                              if selected_card['view_id'] == view_id]
            for selected_card in selected_cards:
                card_index = selected_card['card_index']
                pygame.draw.rect(win, (255, 0, 0), [hand.x[card_index], hand.y, hand.card_width, hand.card_height], 5)

        if view_mode == 'View Trait Piles':
            view_id = game.players[player_id].view_modes[view_mode]
            if view_id == 0:
                view_buttons[0].active = False
            else:
                view_buttons[0].active = True
            if view_id == game.num_players - 1:
                view_buttons[1].active = False
            else:
                view_buttons[1].active = True
            for button in view_buttons:
                if button.active:
                    button.draw(win)

            font = pygame.font.SysFont('comicsans', 20)
            rendered_text = font.render(game.players[view_id].name, 1, (255, 255, 255))
            win.blit(rendered_text, (125, 150 - rendered_text.get_height() / 2))

            trait_pile = TraitPile(game.players[view_id].trait_pile, win_width=game_window.get_width(),
                                   win_height=game_window.get_height())
            trait_pile.draw_trait_pile(win)

            selected_cards = [selected_card for selected_card in
                              game.players[player_id].current_selection['View Trait Piles']
                              if selected_card['view_id'] == view_id]

            for selected_card in selected_cards:
                color = selected_card['color']
                color_index = trait_pile.colors.index(color)
                card_index = selected_card['card_index']
                pygame.draw.rect(win, (255, 0, 0), [trait_pile.x[color_index], trait_pile.y[color][card_index],
                                                    trait_pile.card_width, trait_pile.card_height], 5)

        if view_mode == 'View Game Piles':
            playmat = Playmat(game.discard_pile, game.traits_pile, game.ages_pile, game.eras,
                              win_width=game_window.get_width(), win_height=game_window.get_height())
            playmat.draw_game_piles(win)

        if view_mode == 'View Game State':

            Button(f'Game ended!', 100, 200, (255, 255, 255), 20, 20, 20).draw(win)

            text_world_end = 'World end points: '
            text_face_values = 'Face value points: '
            text_bonus_points = 'Bonus points: '
            text_final_score = 'Final score: '

            for player_scores in game.scores:
                world_end_score = player_scores['world_end']
                face_value_score = player_scores['face_values']
                bonus_points_score = player_scores['bonus_points']
                final_score = world_end_score + face_value_score + bonus_points_score

                text_world_end += ' ' + str(world_end_score)
                text_face_values += ' ' + str(face_value_score)
                text_bonus_points += ' ' + str(bonus_points_score)
                text_final_score += ' ' + str(final_score)

            Button(text_world_end, 100, 300, (255, 255, 255), 20, 20, 20).draw(win)
            Button(text_face_values, 100, 400, (255, 255, 255), 20, 20, 20).draw(win)
            Button(text_bonus_points, 100, 500, (255, 255, 255), 20, 20, 20).draw(win)
            Button(text_final_score, 100, 600, (255, 255, 255), 20, 20, 20).draw(win)

    elif game.game_state[player_id] in ['Playing', 'Discard', 'Random Discard', 'Play Card', 'Waiting for Players Actions']:
        for button in buttons:
            if button.active_type == 'conditional':
                if button.text in game.active_buttons[player_id]:
                    button.active = True
                else:
                    button.active = False
            if button.active:
                button.draw(win)

        Button(f'Game State: {game.game_state[player_id]}', 700, 100, (255, 255, 255), 10, 10, 10).draw(win)

        if view_mode == 'View Hand':
            view_id = game.players[player_id].view_modes[view_mode]
            if view_id == 0:
                view_buttons[0].active = False
            else:
                view_buttons[0].active = True
            if view_id == game.num_players - 1:
                view_buttons[1].active = False
            else:
                view_buttons[1].active = True
            for button in view_buttons:
                if button.active:
                    button.draw(win)

            font = pygame.font.SysFont('comicsans', 20)
            rendered_text = font.render(game.players[view_id].name, 1, (255, 255, 255))
            win.blit(rendered_text, (125, 150 - rendered_text.get_height() / 2))

            if view_id == player_id:
                hand = Hand(game.players[view_id].hand, win_width=game_window.get_width(),
                            win_height=game_window.get_height())
            else:
                hand = Hand(game.players[view_id].hand, win_width=game_window.get_width(),
                            win_height=game_window.get_height(), view_cards=False)
            hand.draw_hand(win)

            gene_pool = GenePool(game.players[player_id].gene_pool)
            gene_pool.draw_gene_pool(win)

            selected_cards = [selected_card for selected_card in game.players[player_id].current_selection['View Hand']
                              if selected_card['view_id'] == view_id]
            for selected_card in selected_cards:
                card_index = selected_card['card_index']
                pygame.draw.rect(win, (255, 0, 0), [hand.x[card_index], hand.y, hand.card_width, hand.card_height], 5)

        if view_mode == 'View Trait Piles':
            view_id = game.players[player_id].view_modes[view_mode]
            if view_id == 0:
                view_buttons[0].active = False
            else:
                view_buttons[0].active = True
            if view_id == game.num_players - 1:
                view_buttons[1].active = False
            else:
                view_buttons[1].active = True
            for button in view_buttons:
                if button.active:
                    button.draw(win)

            font = pygame.font.SysFont('comicsans', 20)
            rendered_text = font.render(game.players[view_id].name, 1, (255, 255, 255))
            win.blit(rendered_text, (125, 150 - rendered_text.get_height() / 2))

            trait_pile = TraitPile(game.players[view_id].trait_pile, win_width=game_window.get_width(),
                                   win_height=game_window.get_height())
            trait_pile.draw_trait_pile(win)

            selected_cards = [selected_card for selected_card in
                              game.players[player_id].current_selection['View Trait Piles']
                              if selected_card['view_id'] == view_id]

            for selected_card in selected_cards:
                color = selected_card['color']
                color_index = trait_pile.colors.index(color)
                card_index = selected_card['card_index']
                pygame.draw.rect(win, (255, 0, 0), [trait_pile.x[color_index], trait_pile.y[color][card_index],
                                                    trait_pile.card_width, trait_pile.card_height], 5)

        if view_mode == 'View Game Piles':
            playmat = Playmat(game.discard_pile, game.traits_pile, game.ages_pile, game.eras,
                              win_width=game_window.get_width(), win_height=game_window.get_height())
            playmat.draw_game_piles(win)

        if view_mode == 'View Game State':
            full_text = game.get_game_state()
            lines = full_text.split('\n')
            for index, line in enumerate(lines):
                if line.strip() == '':
                    continue
                line = line.strip()
                Button(line, 50, 100 + index * 40, (255, 255, 255), 10, 10, 10).draw(win)

    pygame.display.update()


def main(player_name):
    run = True
    pause = False
    unpause_type = None
    n = Network()
    try:
        n.client.sendall(bytes('connected?', encoding='utf-8'))
        connected = True
    except ConnectionAbortedError:
        connected = False
    if not connected:
        print('ERROR: The player is not connected to the server.')
        sys.exit()
    clock = pygame.time.Clock()
    player_id = int(n.player_id)
    print(f'Hello {player_name}!')

    data = {'function': 'update_name',
            'params': {'player_id': player_id, 'name': player_name}}
    n.send(json.dumps(data))

    view_mode = 'View Hand'
    view_modes = ['View Hand', 'View Trait Piles', 'View Game Piles', 'View Game State']

    while run:
        clock.tick(60)
        try:
            game = n.send('get')
        except:
            print('Error server is offline.')
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False

        if not run:
            break

        if event.type == unpause_type:
            pause = False
        if not pause:
            if event.type == pygame.MOUSEBUTTONDOWN:
                unpause_type = pygame.MOUSEBUTTONUP
                pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.active and button.click(pos):
                        pause = True
                        if button.text in view_modes:
                            view_mode = button.text
                        elif button.text == 'End Turn':
                            data = {'function': 'end_turn',
                                    'params': {'player_id': player_id}}
                            n.send(json.dumps(data))
                        elif button.text == 'Stabilize':
                            data = {'function': 'stabilize',
                                    'params': {'player_id': player_id}}
                            n.send(json.dumps(data))
                        elif button.text == 'Discard':
                            data = {'function': 'discard_selected_card',
                                    'params': {'player_id': player_id}}
                            n.send(json.dumps(data))
                        elif button.text == 'Random Discard':
                            data = {'function': 'discard_random_card',
                                    'params': {'player_id': player_id}}
                            n.send(json.dumps(data))
                        elif button.text == 'Play Card':
                            data = {'function': 'play_selected_card',
                                    'params': {'player_id': player_id, 'trait_pile_id': player_id}}
                            n.send(json.dumps(data))
                for view_button in view_buttons:
                    if view_button.active and view_button.click(pos, game_window):
                        pause = True
                        if view_button.direction == 'left':
                            data = {'function': 'update_view_id',
                                    'params': {'player_id': player_id, 'view_mode': view_mode,
                                               'value': -1}}
                            n.send(json.dumps(data))
                        elif view_button.direction == 'right':
                            data = {'function': 'update_view_id',
                                    'params': {'player_id': player_id, 'view_mode': view_mode, 'value': 1}}
                            n.send(json.dumps(data))
                if view_mode == 'View Hand':
                    view_id = game.players[player_id].view_modes[view_mode]
                    hand = Hand(game.players[view_id].hand, win_width=game_window.get_width(),
                                win_height=game_window.get_height())
                    card_index = hand.click(pos)
                    if game.game_state[player_id] in ['Playing', 'Discard', 'Random Discard', 'Play Card', 'Waiting for Players Actions']:
                        if card_index is not None:
                            pause = True
                            data = {'function': 'update_selection', 'params': {'player_id': player_id,
                                                                               'view_mode': view_mode,
                                                                               'view_id': view_id,
                                                                               'selected_index': card_index}}
                            n.send(json.dumps(data))
                if view_mode == 'View Trait Piles':
                    view_id = game.players[player_id].view_modes[view_mode]
                    trait_pile = TraitPile(game.players[view_id].trait_pile, win_width=game_window.get_width(),
                                           win_height=game_window.get_height())
                    trait_pile_color, card_index = trait_pile.click(pos)
                    if game.game_state[player_id] in ['Playing', 'Discard', 'Random Discard', 'Waiting for Players Actions']:
                        if card_index is not None:
                            pause = True
                            data = {'function': 'update_selection', 'params': {'player_id': player_id,
                                                                               'view_mode': view_mode,
                                                                               'view_id': view_id,
                                                                               'color': trait_pile_color,
                                                                               'selected_index': card_index}}
                            n.send(json.dumps(data))

            redraw_window(game_window, game, player_id, view_mode)


main(player_name=name)
