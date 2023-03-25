import pygame
import os
from PIL import Image


class Button:
    def __init__(self, text, x, y, color, text_size=10, border_x=10, border_y=10, active_type='always'):
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
        font = pygame.font.SysFont('comicsans', self.text_size)
        self.rendered_text = font.render(self.text, 1, (0, 0, 0))
        self.width = self.rendered_text.get_width() + 2 * self.border_x
        self.height = self.rendered_text.get_height() + 2 * self.border_y

    def draw(self, win):

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


class ViewButton:
    def __init__(self, direction, x, y, color, height=50, width=35, active=True):
        self.direction = direction
        self.x = x
        self.y = y
        self.color = color
        self.height = height
        self.width = width
        self.active = active
        self.coordinates = None

    def draw(self, win):
        if self.direction == 'right':
            self.coordinates = [[self.x, self.y], [self.x, self.y + self.height],
                                [self.x + self.width, self.y + self.height / 2]]
        elif self.direction == 'left':
            self.coordinates = [[self.x, self.y], [self.x, self.y + self.height],
                                [self.x - self.width, self.y + self.height / 2]]
        pygame.draw.polygon(win, self.color, self.coordinates)

    def click(self, pos, win):
        if not self.active:
            return False
        x1, y1 = pos
        if pygame.draw.polygon(win, self.color, self.coordinates).collidepoint(x1, y1):
            return True
        else:
            return False


class Hand:
    def __init__(self, cards, card_height=500, aspect_ratio=0.71, border_bottom=25, border_sides=25, win_width=700,
                 win_height=700, view_cards=True):
        self.cards = cards
        self.card_height = card_height
        self.aspect_ratio = aspect_ratio
        self.border_bottom = border_bottom
        self.border_sides = border_sides
        self.win_width = win_width
        self.win_height = win_height
        self.view_cards = view_cards

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
                if self.view_cards:
                    card_img = pygame.image.load(os.path.join(os.getcwd(), 'cards', 'images', f'{card.name}.png'))
                else:
                    card_img = pygame.image.load(os.path.join(os.getcwd(), 'cards', 'images', 'Traits.png'))
                card_img.convert()
                card_img = pygame.transform.smoothscale(card_img, (self.card_width, self.card_height))
                if not card.playable or not self.view_cards:
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
            gene_pool_img = pygame.transform.smoothscale(gene_pool_img, (self.card_width, self.card_height))
        elif orientation == 'landscape':
            new_x = self.x
            new_y = self.y + (self.card_height - self.card_width) / 2
            gene_pool_img = pygame.transform.smoothscale(gene_pool_img, (self.card_height, self.card_width))

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
        self.space_between_cards = int(
            (self.trait_pile_width - self.number_colors * self.card_width) / (self.number_colors - 1))

        self.x = [(self.win_width - self.trait_pile_width) / 2 + i * (self.card_width + self.space_between_cards) for i
                  in range(self.number_colors)]

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
                card_img = pygame.image.load(os.path.join(os.getcwd(), 'cards', 'images', f'{card.name}.png'))
                card_img.convert()
                card_img = pygame.transform.smoothscale(card_img, (self.card_width, self.card_height))
                win.blit(card_img, (x, self.y[color][card_index]))

    def click(self, pos):
        x1, y1 = pos
        for color_index, x in enumerate(self.x):
            color = self.colors[color_index]
            for card_index, y in enumerate(self.y[color]):
                if x <= x1 <= x + self.card_width and y <= y1 <= y + self.card_height:
                    return color, card_index
        else:
            return None, None


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
        playmat_img = pygame.transform.smoothscale(playmat_img, (self.playmat_width, self.playmat_height))
        win.blit(playmat_img, (self.playmat_x, self.playmat_y))

        if self.discard_pile:
            discarded_card_img = pygame.image.load(
                os.path.join(self.img_folder, f'{self.discard_pile[-1].name}.png'))
            discarded_card_img.convert()
            discarded_card_img = pygame.transform.smoothscale(discarded_card_img,
                                                              (self.card_width, self.card_height))
            win.blit(discarded_card_img, (self.discard_pile_x, self.discard_pile_y))

        if self.traits_pile:
            traits_back_img = pygame.image.load(self.traits_back_img_path)
            traits_back_img.convert()
            traits_back_img = pygame.transform.smoothscale(traits_back_img, (self.card_width, self.card_height))
            win.blit(traits_back_img, (self.traits_pile_x, self.traits_pile_y))

        if self.ages_pile:
            ages_back_img = pygame.image.load(self.ages_back_img_path)
            ages_back_img.convert()
            ages_back_img = pygame.transform.smoothscale(ages_back_img, (self.card_width, self.card_height))
            win.blit(ages_back_img, (self.ages_pile_x, self.ages_pile_y))

        for era, cards in enumerate(self.eras):
            if cards:
                card_img = pygame.image.load(os.path.join(self.img_folder, f'{cards[-1].name}.png'))
                card_img.convert()
                card_img = pygame.transform.smoothscale(card_img, (self.card_width, self.card_height))
                win.blit(card_img, (self.eras_x_y[era][0], self.eras_x_y[era][1]))

    def click(self, pos):
        pass
