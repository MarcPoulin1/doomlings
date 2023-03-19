from cards.traits import traits
from cards.ages import ages, birth_of_life
from cards.catastrophes import catastrophes
import random
import inspect


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.trait_pile_colors = ['Purple', 'Blue', 'Red', 'Green', 'Colorless']
        self.trait_pile = {color: [] for color in self.trait_pile_colors}
        self.number_cards_turn = 1
        self.hand = []
        self.gene_pool = 0
        self.name = None
        self.number_cards_to_discard = 0
        self.stabilized = False
        self.discard_index = None
        self.number_dominants = 0
        self.world_end_points = 0

    def number_cards_in_hand(self):
        return len(self.hand)

    def number_colors(self):
        num_colors = 0
        for color, cards in self.trait_pile.items():
            if color != 'Colorless':
                if len(cards) > 0:
                    num_colors += 1
        return num_colors

    def number_traits(self, color=None):
        if color is None:
            return sum({key: len(values) for key, values in self.trait_pile.items()}.values())
        elif color not in self.trait_pile_colors:
            raise Exception('Color in not found in possible colors.')
        else:
            return sum({color: len(values) for key, values in self.trait_pile.items() if key == color}.values())


class Game:
    def __init__(self, num_players, age_per_pile=3, num_eras=3, max_gene_pool=8, min_gene_pool=1):
        self.world_ended = False
        self.last_discard_player_id = None
        self.last_discarded_card = None
        self.connected_players = 0
        self.turn = None
        self.active_player = None
        self.traits = traits
        self.ages = ages
        self.catastrophes = catastrophes
        self.last_trait_played = None
        self.last_player_id = None
        self.players = [Player(player_id) for player_id in range(num_players)]
        self.discard_pile = []
        self.ages_pile = []
        self.traits_pile = self.traits.copy()
        self.age_per_pile = age_per_pile
        self.num_eras = num_eras
        self.current_era = 0
        self.eras = [[] for _ in range(self.num_eras)]
        self.num_players = num_players
        self.active_buttons = [[] for _ in range(self.num_players)]
        self.scores = [{'world_end': 0, 'face_values': 0, 'bonus_points': 0} for _ in range(self.num_players)]
        self.game_state = ['Waiting for players' for _ in range(self.num_players)]
        self.turn_restrictions = []

        self.max_gene_pool = max_gene_pool
        self.min_gene_pool = min_gene_pool

    def start_game(self):

        random.shuffle(self.traits_pile)
        self.select_age_pile()
        self.turn = 0
        self.active_player = 0
        self.active_buttons = [['Stabilize'], []]
        self.start_new_turn()

        self.hand_playable()

    def select_age_pile(self):
        # select the cards used for the age pile
        selected_ages = random.sample(self.ages, self.age_per_pile * self.num_eras)
        selected_catastrophes = random.sample(self.catastrophes, self.num_eras)

        selected_ages_piles = [selected_ages[start:start + self.age_per_pile] for start in range(0, len(selected_ages),
                                                                                                 self.age_per_pile)]

        for index, (a, c) in enumerate(zip(selected_ages_piles, selected_catastrophes)):
            selected_ages_piles[index].append(c)
            random.shuffle(selected_ages_piles[index])

        combined_age_pile = []
        for age_pile in selected_ages_piles:
            combined_age_pile += age_pile

        self.ages_pile = [birth_of_life] + combined_age_pile

    def play_card(self, player_id, trait_pile_id, card_index):
        played_card = self.players[player_id].hand[card_index]
        self.last_trait_played = played_card
        self.last_player_id = player_id

        self.players[trait_pile_id].trait_pile[played_card.color] += [played_card]
        if played_card.is_dominant:
            self.players[player_id].number_dominants += 1
        del self.players[player_id].hand[card_index]
        self.players[player_id].number_cards_turn -= 1

        for effect in played_card.effects:
            function_name = effect['name']
            params = effect['params']
            game_function = getattr(self, function_name)
            if 'player_id' in inspect.getfullargspec(game_function).args:
                params['player_id'] = player_id
            if 'trait_pile_id' in inspect.getfullargspec(game_function).args:
                params['trait_pile_id'] = trait_pile_id
            game_function(**params)

        self.hand_playable()

    def end_turn(self, player_id):
        start_new_turn = False
        self.players[player_id].stabilized = False
        self.active_player += 1
        if self.active_player == self.num_players:
            start_new_turn = True
            self.turn += 1
            self.active_player = 0

        self.players[self.active_player].number_cards_turn = 1
        self.active_buttons[player_id] = []
        self.active_buttons[self.active_player] = ['Stabilize']
        if start_new_turn:
            self.start_new_turn()
        self.hand_playable()

    def start_new_turn(self):
        self.turn_restrictions = []
        active_age = self.ages_pile[0]
        del self.ages_pile[0]
        self.eras[self.current_era].append(active_age)

        if type(active_age).__name__ == 'Catastrophe':
            self.current_era += 1

            self.modify_gene_pool(affected_players='all', value=active_age.gene_pool_effect)

            for effect in active_age.catastrophe_effects:
                function_name = effect['name']
                params = effect['params']
                game_function = getattr(self, function_name)
                game_function(**params)

            self.hand_playable()

            if self.current_era == self.num_eras:
                if sum([player.number_cards_to_discard for player in self.players]) > 0:
                    self.world_ended = True
                else:
                    self.world_end()
        else:
            for effect in active_age.instant_effects:
                function_name = effect['name']
                params = effect['params']
                game_function = getattr(self, function_name)
                game_function(**params)

            for effect in active_age.turn_effects:
                function_name = effect['name']
                params = effect['params']
                game_function = getattr(self, function_name)
                game_function(**params)
            self.hand_playable()

    def world_end(self):

        for player_id, player in enumerate(self.players):
            self.resolve_word_end_traits(player_id)

        self.resolve_world_end_effect()

        self.compile_score()

        self.game_state = ['End game' for _ in range(self.num_players)]

        print('world ended!')

    def resolve_word_end_traits(self, player_id):
        pass

    def resolve_world_end_effect(self):
        pass

    def compile_score(self):

        for player_id, player in enumerate(self.players):
            # world end points
            self.scores[player_id]['world_end'] = 0

            # face value points
            for color, cards in player.trait_pile.items():
                for card in cards:
                    self.scores[player_id]['face_values'] += card.face_value

            # bonus points
            self.scores[player_id]['bonus_points'] = 0

    def catastrophe(self):
        pass

    def modify_gene_pool(self, affected_players, value, trait_pile_id=None):
        if affected_players == 'all':
            for player in self.players:
                player.gene_pool = max(min(self.max_gene_pool, player.gene_pool + value), self.min_gene_pool)
        elif affected_players == 'opponents':
            for p_id, player in enumerate(self.players):
                if p_id != trait_pile_id:
                    player.gene_pool = max(min(self.max_gene_pool, player.gene_pool + value), self.min_gene_pool)
        elif affected_players == 'self':
            self.players[trait_pile_id].gene_pool = max(min(self.max_gene_pool, self.players[trait_pile_id].gene_pool + value), self.min_gene_pool)

    def hand_playable(self):
        for player_id, player in enumerate(self.players):
            if player_id == self.active_player:
                if player.number_cards_turn > 0:
                    for card in player.hand:
                        if self.turn_restricted(card):
                            card.playable = False
                        elif card.is_dominant and player.number_dominants == 2:
                            card.playable = False
                        else:
                            card.playable = True
                else:
                    for card in player.hand:
                        card.playable = False
            else:
                for card in player.hand:
                    card.playable = False

    def stabilize(self, player_id):
        player = self.players[player_id]
        num_cards_to_draw = player.gene_pool - player.number_cards_in_hand()
        self.players[player_id].stabilized = True
        if num_cards_to_draw > 0:
            self.draw_cards('self', num_cards_to_draw, player_id)
            self.active_buttons[player_id] = ['End Turn']
        elif num_cards_to_draw < 0:
            num_cards_to_discard = -num_cards_to_draw
            self.players[player_id].number_cards_to_discard = min(num_cards_to_discard, player.number_cards_in_hand())
            if sum([player.number_cards_to_discard for player in self.players]) > 0:
                self.update_discard_state()
        else:
            self.active_buttons[player_id] = ['End Turn']

        player.number_cards_turn = 0
        self.hand_playable()

    def stabilize_all_players(self, reset_stabilize):
        for player_id in range(self.num_players):
            self.stabilize(player_id)
            if reset_stabilize:
                self.players[player_id].stabilized = False
                if player_id == self.active_player:
                    self.active_buttons[player_id] = ['Stabilize']
                else:
                    self.active_buttons[player_id] = []

    def draw_cards(self, affected_players, value, player_id=None):
        if affected_players == 'all':
            for player in self.players:
                drawn_cards = self.traits_pile[:value]
                self.traits_pile = self.traits_pile[value:]
                player.hand += drawn_cards
        elif affected_players == 'opponents':
            for p_id, player in enumerate(self.players):
                if p_id != player_id:
                    drawn_cards = self.traits_pile[:value]
                    self.traits_pile = self.traits_pile[value:]
                    player.hand += drawn_cards
        elif affected_players == 'self':
            drawn_cards = self.traits_pile[:value]
            self.traits_pile = self.traits_pile[value:]
            self.players[player_id].hand += drawn_cards

        self.hand_playable()

    def update_name(self, player_id, name):
        self.players[player_id].name = name

        connected_players = 0
        for player in self.players:
            if player.name is not None:
                connected_players += 1
        self.connected_players = connected_players

        if self.connected_players == self.num_players:
            if self.game_state[0] == 'Waiting for players':
                self.start_game()
                self.game_state = ['Playing' for _ in range(self.num_players)]

    def update_discard_selection(self, player_id, card_index):
        if self.players[player_id].discard_index == card_index:
            self.players[player_id].discard_index = None
        else:
            self.players[player_id].discard_index = card_index

    def discard_selected_card(self, player_id):
        player = self.players[player_id]
        discarded_card = player.hand[player.discard_index]
        player.number_cards_to_discard -= 1
        self.discard_pile.append(discarded_card)
        del player.hand[player.discard_index]
        player.discard_index = None
        self.last_discarded_card = discarded_card
        self.last_discard_player_id = player_id
        if sum([player.number_cards_to_discard for player in self.players]) == 0:
            for player_id, player in enumerate(self.players):
                if self.world_ended:
                    self.world_end()
                else:
                    self.game_state[player_id] = 'Playing'
                if player_id == self.active_player:
                    if player.stabilized:
                        self.active_buttons[player_id] = ['End Turn']
                    elif player_id == self.active_player:
                        self.active_buttons[player_id] = ['Stabilize']
                else:
                    self.active_buttons[player_id] = []
        else:
            self.update_discard_state()
        self.hand_playable()

    def add_turn_restriction(self, restricted_attribute, restricted_value, restricted_type):
        self.turn_restrictions.append({'restricted_attribute': restricted_attribute,
                                       'restricted_value': restricted_value,
                                       'restricted_type': restricted_type})

    def modify_number_cards_to_discard(self, affected_players, value):
        if affected_players == 'all':
            for player_id, player in enumerate(self.players):
                player.number_cards_to_discard = min(value, player.number_cards_in_hand())

        if sum([player.number_cards_to_discard for player in self.players]) > 0:
            self.update_discard_state()

    def turn_restricted(self, card):
        for restriction in self.turn_restrictions:
            if restriction['restricted_type'] == 'equal':
                if getattr(card, restriction['restricted_attribute']) == restriction['restricted_value']:
                    return True
            elif restriction['restricted_type'] == 'greater_than':
                if getattr(card, restriction['restricted_attribute']) > restriction['restricted_value']:
                    return True
            elif restriction['restricted_type'] == 'smaller_than':
                if getattr(card, restriction['restricted_attribute']) < restriction['restricted_value']:
                    return True
        return False

    def modify_number_cards_turn(self, affected_players, value):
        if affected_players == 'all':
            for player in self.players:
                player.number_cards_turn = value

    def discard_hand(self, affected_players, player_id=None):
        if affected_players == 'self':
            player = self.players[player_id]
            discarded_cards = player.hand
            self.discard_pile += discarded_cards
            player.hand = []
            self.last_discarded_card = discarded_cards[-1]
            self.last_discard_player_id = player_id
            self.hand_playable()

    def skip_stabilization(self, affected_players, player_id=None):
        if affected_players == 'self':
            self.active_buttons[player_id] = ['End Turn']

    def draw_card_for_every_color_type(self, affected_players):
        if affected_players == 'all':
            for player_id, player in enumerate(self.players):
                num_cards_to_draw = player.number_colors()
                self.draw_cards('self', num_cards_to_draw, player_id=player_id)

    def discard_card_from_hand_for_every_color(self, affected_players, color):
        if affected_players == 'all':
            for player_id, player in enumerate(self.players):
                num_cards_to_discard = player.number_traits(color)
                player.number_cards_to_discard = min(num_cards_to_discard, player.number_cards_in_hand())

        if sum([player.number_cards_to_discard for player in self.players]) > 0:
            self.update_discard_state()

    def discard_card_from_hand_for_every_dominant(self, affected_players):
        if affected_players == 'all':
            for player_id, player in enumerate(self.players):
                num_cards_to_discard = player.number_dominants
                if num_cards_to_discard > 0:
                    player.number_cards_to_discard = min(num_cards_to_discard, player.number_cards_in_hand())

        if sum([player.number_cards_to_discard for player in self.players]) > 0:
            self.update_discard_state()

    def update_discard_state(self):
        first_player_to_discard = [i for i, player in enumerate(self.players) if player.number_cards_to_discard][0]
        for player_id, player in enumerate(self.players):
            if player_id == first_player_to_discard:
                self.active_buttons[player_id] = ['Discard']
                self.game_state[player_id] = 'Discard'
            else:
                self.game_state[player_id] = 'Waiting for Players to Discard'
                self.active_buttons[player_id] = ['Waiting for Players to Discard']

    def get_game_state(self):

        ages_pile_names = [age.name for age in self.ages_pile]
        discard_pile_names = [card.name for card in self.discard_pile]
        traits_pile_names = [trait.name for trait in self.traits_pile]

        players_hand_names = [[] for _ in range(self.num_players)]
        for player_id in range(self.num_players):
            for card in self.players[player_id].hand:
                players_hand_names[player_id].append(card.name)

        players_trait_pile_names = [{color: [] for color in self.players[player_id].trait_pile_colors} for player_id in
                                    range(self.num_players)]
        for player_id in range(self.num_players):
            for color in self.players[player_id].trait_pile_colors:
                for card in self.players[player_id].trait_pile[color]:
                    players_trait_pile_names[player_id][color].append(card.name)

        general_text = f"""
                        General information:
                        Number of players: {self.num_players}
                        Age pile cards: {ages_pile_names}
                        Discard pile cards: {discard_pile_names}
                        Trait pile cards: {traits_pile_names}
                        """

        displayed_text = general_text
        for player_id in range(self.num_players):
            displayed_text += f"""Player {player_id}:
                                Cards in hand: {players_hand_names[player_id]}
                                Cards in trait pile: {players_trait_pile_names[player_id]}
                                """
        self.compile_score()
        displayed_text += str(self.scores)
        for player_id in range(self.num_players):
            cards_playable = [card.playable for card in self.players[player_id].hand]
            displayed_text += str(cards_playable)

        return displayed_text
