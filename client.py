import pygame
from network import Network
import sys
import json
import os
from PIL import Image

name = input('Enter your player name:')

pygame.font.init()

window_width = 700
window_height = 700

game_window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE, depth=64)


class Button:
    def __init__(self, text, x, y, color, text_size=10, border_x=10, border_y=10, active_type='always'):
        self.width = None
        self.height = None
        self.rendered_text = None
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.text_size = text_size
        self.border_x = border_x
        self.border_y = border_y
        self.active_type = active_type
        self.active = True

    def draw(self, win):
        font = pygame.font.SysFont('comicsans', self.text_size)
        self.rendered_text = font.render(self.text, 1, (0, 0, 0))
        self.width = self.rendered_text.get_width() + 2 * self.border_x
        self.height = self.rendered_text.get_height() + 2 * self.border_y

        pygame.draw.rect(win, self.color, (self.x - self.border_x, self.y - self.border_y, self.width, self.height))
        win.blit(self.rendered_text, (self.x, self.y))

    def click(self, pos):
        if not self.active:
            return False
        x1, y1 = pos
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


class Hand:
    def __init__(self, cards, card_height=500, aspect_ratio=0.71, border_bottom=25, border_sides=25, win_width=700,
                 win_height=700):
        self.cards = cards
        self.card_height = card_height
        self.aspect_ratio = aspect_ratio
        self.border_bottom = border_bottom
        self.border_sides = border_sides
        self.win_width = win_width
        self.win_height = win_height

        self.number_cards = len(self.cards)
        self.card_max_width = self.card_height * self.aspect_ratio
        self.hand_max_width = self.win_width - 2 * self.border_sides
        if self.number_cards == 0:
            self.card_width = self.card_max_width
        else:
            self.card_width = min(self.card_max_width, self.hand_max_width / self.number_cards)
        self.card_height = min(self.card_height, self.card_width / self.aspect_ratio)
        self.hand_width = self.card_width * self.number_cards

        self.x = [int((self.win_width - self.hand_width) / 2 + i * self.card_width) for i in range(self.number_cards)]
        self.y = self.win_height - self.border_bottom - self.card_height

    def draw_hand(self, win):
        if self.number_cards == 0:
            pass
        else:
            for card_index, card in enumerate(self.cards):
                card_img = pygame.image.load(os.path.join(os.getcwd(), 'cards', 'images',  f'{card.name}.png'))
                card_img.convert()
                card_img = pygame.transform.scale(card_img, (self.card_width, self.card_height))
                if not card.playable:
                    card_img.set_alpha(128)
                win.blit(card_img, (self.x[card_index], self.y))

    def click(self, pos):
        x1, y1 = pos
        for card_index, x in enumerate(self.x):
            if x <= x1 <= x + self.card_width and self.y <= y1 <= self.y + self.card_height:
                return card_index
        else:
            return None


class GenePool:
    def __init__(self, gene_pool_value, card_height=200, aspect_ratio=0.71, x=50, y=200,
                 img_folder=os.path.join(os.getcwd(), 'cards', 'images')):
        self.gene_pool_value = gene_pool_value
        self.card_height = card_height
        self.aspect_ratio = aspect_ratio
        self.x = x
        self.y = y
        self.img_folder = img_folder

        self.card_width = card_height * aspect_ratio

    def draw_gene_pool(self, win):
        gene_pool_img_path = os.path.join(self.img_folder, f'Gene Pool {self.gene_pool_value}.png')
        gene_pool_img = pygame.image.load(gene_pool_img_path)
        gene_pool_img.convert()

        if self.gene_pool_value >= 5:
            if (self.gene_pool_value - 5) % 2:
                orientation = 'landscape'
            else:
                orientation = 'portrait'
        else:
            if (4 - self.gene_pool_value) % 2:
                orientation = 'landscape'
            else:
                orientation = 'portrait'

        if orientation == 'portrait':
            new_x = self.x + (self.card_height - self.card_width) / 2
            new_y = self.y
            gene_pool_img = pygame.transform.scale(gene_pool_img, (self.card_width, self.card_height))
        elif orientation == 'landscape':
            new_x = self.x
            new_y = self.y + (self.card_height - self.card_width) / 2
            gene_pool_img = pygame.transform.scale(gene_pool_img, (self.card_height, self.card_width))

        win.blit(gene_pool_img, (new_x, new_y))

    def click(self, pos):
        pass


class TraitPile:
    def __init__(self, trait_pile, card_max_height=200, aspect_ratio=0.71, border_bottom=25, border_top=100,
                 border_sides=25, win_width=700, win_height=700):
        self.trait_pile = trait_pile
        self.card_max_height = card_max_height
        self.aspect_ratio = aspect_ratio
        self.border_bottom = border_bottom
        self.border_top = border_top
        self.border_sides = border_sides
        self.win_width = win_width
        self.win_height = win_height

        self.colors = list(self.trait_pile.keys())
        self.number_colors = len(self.trait_pile.keys())
        self.number_cards = {key: len(value) for key, value in self.trait_pile.items()}
        self.card_max_width = self.card_max_height * self.aspect_ratio
        self.trait_pile_width = self.win_width - 2 * self.border_sides
        self.card_width = int(min(self.card_max_width, self.trait_pile_width / self.number_colors))
        self.card_height = int(min(self.card_max_height, self.card_width / self.aspect_ratio))
        self.space_between_cards = int((self.trait_pile_width - self.number_colors * self.card_width) / (self.number_colors - 1))

        self.x = [(self.win_width - self.trait_pile_width) / 2 + i * (self.card_width + self.space_between_cards) for i in range(self.number_colors)]

        color_pile_height = self.win_height - self.border_bottom - self.border_top - self.card_height
        self.y = {key: [] for key, value in self.trait_pile.items()}
        for key, value in self.trait_pile.items():
            if self.number_cards[key] == 0:
                continue
            elif self.number_cards[key] == 1:
                y_step = 0
                start_y = self.win_height - self.border_bottom - self.card_height
            else:
                y_step = min(self.card_height, (color_pile_height / (self.number_cards[key] - 1)))
                start_y = self.win_height - self.border_bottom - self.card_height
            self.y[key] = [int(start_y - i * y_step) for i in range(self.number_cards[key])]

    def draw_trait_pile(self, win):
        for color_index in range(self.number_colors):
            x = self.x[color_index]
            color = self.colors[color_index]
            for card_index, card in enumerate(self.trait_pile[color]):
                card_img = pygame.image.load(os.path.join(os.getcwd(), 'cards', 'images',  f'{card.name}.png'))
                card_img.convert()
                card_img = pygame.transform.scale(card_img, (self.card_width, self.card_height))
                win.blit(card_img, (x, self.y[color][card_index]))

    def click(self, pos):
        pass


class Playmat:
    def __init__(self, discard_pile, traits_pile, ages_pile, eras, border_bottom=25, border_top=100, border_sides=25,
                 win_width=700, win_height=700, img_folder=os.path.join(os.getcwd(), 'cards', 'images')):
        self.discard_pile = discard_pile
        self.traits_pile = traits_pile
        self.ages_pile = ages_pile
        self.eras = eras
        self.border_bottom = border_bottom
        self.border_top = border_top
        self.border_sides = border_sides
        self.win_width = win_width
        self.win_height = win_height
        self.img_folder = img_folder

        self.ages_back_img_path = os.path.join(self.img_folder, 'Ages.png')
        self.traits_back_img_path = os.path.join(self.img_folder, 'Traits.png')
        self.playmat_img_path = os.path.join(self.img_folder, 'Playmat.png')

        with Image.open(self.playmat_img_path) as playmat_img:
            self.playmat_original_width, self.playmat_original_height = playmat_img.size
            self.playmat_aspect_ratio = self.playmat_original_width / self.playmat_original_height

        self.playmat_max_width = self.win_width - 2 * self.border_sides
        self.playmat_max_height = self.win_height - self.border_top - self.border_bottom
        self.playmat_space_aspect_ratio = self.playmat_max_width / self.playmat_max_height

        if self.playmat_space_aspect_ratio <= self.playmat_aspect_ratio:
            self.playmat_width = self.playmat_max_width
            self.playmat_height = int(self.playmat_width / self.playmat_aspect_ratio)
        else:
            self.playmat_height = self.playmat_max_height
            self.playmat_width = int(self.playmat_height * self.playmat_aspect_ratio)

        self.playmat_x = (self.win_width - self.playmat_width) / 2
        self.playmat_y = (self.win_height - self.playmat_height) / 2

        self.card_width = int(186 / self.playmat_original_width * self.playmat_width)
        self.card_height = int(259 / self.playmat_original_height * self.playmat_height)

        self.discard_pile_x = self.get_coordinate_from_original(190, 'x')
        self.discard_pile_y = self.get_coordinate_from_original(386, 'y')

        self.traits_pile_x = self.get_coordinate_from_original(410, 'x')
        self.traits_pile_y = self.get_coordinate_from_original(386, 'y')

        self.ages_pile_x = self.get_coordinate_from_original(712, 'x')
        self.ages_pile_y = self.get_coordinate_from_original(386, 'y')

        self.eras_x_y = [[self.get_coordinate_from_original(933, 'x'), self.get_coordinate_from_original(386, 'y')],
                         [self.get_coordinate_from_original(1153, 'x'), self.get_coordinate_from_original(386, 'y')],
                         [self.get_coordinate_from_original(1374, 'x'), self.get_coordinate_from_original(386, 'y')]]

    def get_coordinate_from_original(self, original_coordinate, dim):
        if dim == 'x':
            return int(self.playmat_x + (original_coordinate / self.playmat_original_width) * self.playmat_width)
        else:
            return int(self.playmat_y + (original_coordinate / self.playmat_original_height) * self.playmat_height)

    def draw_game_piles(self, win):
        self.playmat_img_path = os.path.join(self.img_folder, 'Playmat.png')
        playmat_img = pygame.image.load(self.playmat_img_path)
        playmat_img.convert()
        playmat_img = pygame.transform.scale(playmat_img, (self.playmat_width, self.playmat_height))
        win.blit(playmat_img, (self.playmat_x, self.playmat_y))

        if self.discard_pile:
            discarded_card_img = pygame.image.load(self.discard_pile[-1].img_path)
            discarded_card_img.convert()
            discarded_card_img = pygame.transform.scale(discarded_card_img, (self.card_width, self.card_height))
            win.blit(discarded_card_img, (self.discard_pile_x, self.discard_pile_y))

        if self.traits_pile:
            traits_back_img = pygame.image.load(self.traits_back_img_path)
            traits_back_img.convert()
            traits_back_img = pygame.transform.scale(traits_back_img, (self.card_width, self.card_height))
            win.blit(traits_back_img, (self.traits_pile_x, self.traits_pile_y))

        if self.ages_pile:
            ages_back_img = pygame.image.load(self.ages_back_img_path)
            ages_back_img.convert()
            ages_back_img = pygame.transform.scale(ages_back_img, (self.card_width, self.card_height))
            win.blit(ages_back_img, (self.ages_pile_x, self.ages_pile_y))

        for era, cards in enumerate(self.eras):
            if cards:
                card_img = pygame.image.load(cards[-1].img_path)
                card_img.convert()
                card_img = pygame.transform.scale(card_img, (self.card_width, self.card_height))
                win.blit(card_img, (self.eras_x_y[era][0], self.eras_x_y[era][1]))

    def click(self, pos):
        pass


buttons = [Button('View Hand', 50, 50, (255, 255, 255), 10, 10, 10),
           Button('View Trait Piles', 150, 50, (255, 255, 255), 10, 10, 10),
           Button('View Game Piles', 250, 50, (255, 255, 255), 10, 10, 10),
           Button('View Game State', 350, 50, (255, 255, 255), 10, 10, 10),
           Button('Discard', 350, 100, (255, 255, 255), 10, 10, 10, 'conditional'),
           Button('Waiting for Players to Discard', 700, 100, (255, 255, 255), 10, 10, 10, 'conditional'),
           Button('Stabilize', 450, 100, (255, 255, 255), 10, 10, 10, 'conditional'),
           Button('End Turn', 550, 100, (255, 255, 255), 10, 10, 10, 'conditional')]


def redraw_window(win, game, player_id, view_mode):

    win.fill((0, 0, 0))

    if game.game_state[player_id] == 'Waiting for players':
        Button(f'Waiting for all players to connect: {game.connected_players}/{game.num_players}',
               100, 100, (255, 255, 255), 20, 20, 20).draw(win)
    if game.game_state[player_id] == 'End game':

        Button(f'Game ended!', 100, 100, (255, 255, 255), 20, 20, 20).draw(win)

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

        Button(text_world_end, 100, 100, (255, 255, 255), 20, 20, 20).draw(win)
        Button(text_face_values, 100, 200, (255, 255, 255), 20, 20, 20).draw(win)
        Button(text_bonus_points, 100, 300, (255, 255, 255), 20, 20, 20).draw(win)
        Button(text_final_score, 100, 400, (255, 255, 255), 20, 20, 20).draw(win)

    elif game.game_state[player_id] in ['Playing', 'Discard', 'Waiting for Players to Discard']:
        for button in buttons:
            if button.active_type == 'conditional':
                if button.text in game.active_buttons[player_id]:
                    button.active = True
                else:
                    button.active = False
            if button.active:
                button.draw(win)

        if view_mode == 'View Hand':
            hand = Hand(game.players[player_id].hand, win_width=game_window.get_width(), win_height=game_window.get_height())
            hand.draw_hand(win)

            gene_pool = GenePool(game.players[player_id].gene_pool)
            gene_pool.draw_gene_pool(win)

            Button(f'Gene Pool: {game.players[player_id].gene_pool}', 250, 100, (255, 255, 255), 10, 10, 10).draw(win)

            if game.game_state[player_id] == 'Discard':
                Button(f'{game.players[player_id].number_cards_to_discard} card(s) left to discard', 500, 100, (255, 255, 255), 10, 10, 10).draw(win)
                discard_index = game.players[player_id].discard_index
                if discard_index is not None:
                    pygame.draw.rect(win, (255, 0, 0), [hand.x[discard_index], hand.y, hand.card_width, hand.card_height], 5)

        if view_mode == 'View Trait Piles':
            trait_pile = TraitPile(game.players[player_id].trait_pile, win_width=game_window.get_width(), win_height=game_window.get_height())
            trait_pile.draw_trait_pile(win)

        if view_mode == 'View Game Piles':
            playmat = Playmat(game.discard_pile, game.traits_pile, game.ages_pile, game.eras, win_width=game_window.get_width(), win_height=game_window.get_height())
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

    data = {'action': 'update_name',
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

        hand = Hand(game.players[player_id].hand, win_width=game_window.get_width(), win_height=game_window.get_height())

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
                    if button.click(pos):
                        pause = True
                        if button.text in view_modes:
                            view_mode = button.text
                        elif button.text == 'End Turn':
                            data = {'action': 'end_turn',
                                    'params': {'player_id': player_id}}
                            n.send(json.dumps(data))
                        elif button.text == 'Stabilize':
                            data = {'action': 'stabilize',
                                    'params': {'player_id': player_id}}
                            n.send(json.dumps(data))
                        elif button.text == 'Discard':
                            if game.players[player_id].discard_index is not None:
                                data = {'action': 'discard_selected_card',
                                        'params': {'player_id': player_id}}
                                n.send(json.dumps(data))
                card_index = hand.click(pos)
                if game.game_state[player_id] == 'Playing':
                    if card_index is not None:
                        pause = True
                        if game.players[player_id].hand[card_index].playable:
                            data = {'action': 'play_card', 'params': {'player_id': player_id, 'trait_pile_id': player_id,
                                                                      'card_index': card_index}}
                            n.send(json.dumps(data))
                elif game.game_state[player_id] == 'Discard':
                    if card_index is not None:
                        pause = True
                        data = {'action': 'update_discard_selection', 'params': {'player_id': player_id,
                                                                                 'card_index': card_index}}
                        n.send(json.dumps(data))

            redraw_window(game_window, game, player_id, view_mode)


main(player_name=name)
