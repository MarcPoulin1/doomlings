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
        self.stabilized = False
        self.number_dominants = 0
        self.world_end_points = 0
        self.bonus_points = 0
        self.view_modes = {'View Hand': player_id, 'View Trait Piles': player_id}

    def number_cards_in_hand(self, card_type='all'):
        if card_type == 'dominant':
            card_count = 0
            for card in self.hand:
                if card.is_dominant:
                    card_count += 1
            return card_count
        elif card_type == 'effect':
            card_count = 0
            for card in self.hand:
                if card.effects is not None or card.remove_effects is not None or card.bonus_points is not None:
                    card_count += 1
            return card_count
        elif card_type == 'all':
            return len(self.hand)

    def number_cards_playable(self):
        card_count = 0
        for card in self.hand:
            if card.playable:
                card_count += 1
        return card_count

    def number_colors(self, location):
        num_colors = 0
        if location == 'trait_pile':
            for color, cards in self.trait_pile.items():
                if color != 'Colorless':
                    if len(cards) > 0:
                        num_colors += 1
            return num_colors
        elif location == 'hand':
            colors = []
            for card in self.hand:
                if card.color != 'Colorless' and card.color not in colors:
                    colors.append(card.color)
            return len(colors)

    def lowest_color_count(self):
        number_cards_color = [len(values) for values in self.trait_pile.values() if len(values) > 0]
        if number_cards_color:
            return min([len(values) for values in self.trait_pile.values() if len(values) > 0])
        else:
            return 0

    def number_traits(self, color=None):
        if color is None:
            return sum([len(values) for values in self.trait_pile.values()])
        elif color not in self.trait_pile_colors:
            raise Exception('Color in not found in possible colors.')
        else:
            return sum([len(values) for key, values in self.trait_pile.items() if key == color])

    def number_traits_above(self, face_value):
        number_traits = 0
        for traits in self.trait_pile.values():
            for trait in traits:
                if trait.face_value is not None and trait.face_value > face_value:
                    number_traits += 1
        return number_traits

    def number_traits_equal(self, face_value):
        number_traits = 0
        for traits in self.trait_pile.values():
            for trait in traits:
                if trait.face_value is not None and trait.face_value == face_value:
                    number_traits += 1
        return number_traits

    def number_traits_negative(self):
        number_traits = 0
        for traits in self.trait_pile.values():
            for trait in traits:
                if trait.face_value is not None and trait.face_value < 0:
                    number_traits += 1
        return number_traits

    def number_traits_expansion(self, expansion):
        number_traits = 0
        for traits in self.trait_pile.values():
            for trait in traits:
                if trait.expansion == expansion:
                    number_traits += 1
        return number_traits

    def number_kidneys(self):
        number_traits = 0
        for traits in self.trait_pile.values():
            for trait in traits:
                if trait.name.startswith('Kidney'):
                    number_traits += 1
        return number_traits

    def number_swarms(self):
        number_traits = 0
        for traits in self.trait_pile.values():
            for trait in traits:
                if trait.name.startswith('Swarm'):
                    number_traits += 1
        return number_traits

    def at_least_n_traits(self, num_traits, color):
        if self.number_traits(color) >= num_traits:
            return True
        else:
            return False


class Game:
    def __init__(self, num_players, age_per_pile=1, num_eras=3, max_gene_pool=8, min_gene_pool=1):
        self.end_turn_number_cards = None
        self.ignore_actions = False
        self.scored_compiled = False
        self.world_end_effect = None
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
        for player in self.players:
            player.current_selection = {'View Hand': [],
                                        'View Trait Piles': []}
        self.action_queue = []

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

    def play_selected_card(self, player_id, trait_pile_id):
        player = self.players[player_id]
        if self.action_queue and self.action_queue[0]['name'] == 'Play Card':
            ignore_actions = self.action_queue[0]['ignore_actions']
            del self.action_queue[0]
        else:
            ignore_actions = False
        if self.ignore_actions:
            ignore_actions = True
        selected_card_index = player.current_selection['View Hand'][0]['card_index']
        played_card = player.hand[selected_card_index]
        self.last_trait_played = played_card
        self.last_player_id = player_id

        self.players[trait_pile_id].trait_pile[played_card.color] += [played_card]
        if played_card.is_dominant:
            player.number_dominants += 1
        del player.hand[selected_card_index]
        player.number_cards_turn -= 1

        if played_card.effects is not None:
            for effect in played_card.effects:
                function_name = effect['name']
                params = effect['params']
                game_function = getattr(self, function_name)
                if 'player_id' in inspect.getfullargspec(game_function).args:
                    params['player_id'] = player_id
                if 'trait_pile_id' in inspect.getfullargspec(game_function).args:
                    params['trait_pile_id'] = trait_pile_id
                game_function(**params)
                self.reset_selections(player_id)
                self.update_game()

        if played_card.actions is not None and not ignore_actions:
            for action in played_card.actions:
                function_name = action['name']
                params = action['params']
                game_function = getattr(self, function_name)
                if 'player_id' in inspect.getfullargspec(game_function).args:
                    params['player_id'] = player_id
                if 'trait_pile_id' in inspect.getfullargspec(game_function).args:
                    params['trait_pile_id'] = trait_pile_id
                game_function(**params)
                self.reset_selections(player_id)
                self.update_game()

        self.reset_selections(player_id)
        self.update_game()

    def end_turn(self, player_id):
        player = self.players[player_id]
        if self.end_turn_number_cards is not None:
            num_cards_to_draw = self.end_turn_number_cards - player.number_cards_in_hand()
            if num_cards_to_draw > 0:
                self.draw_cards('self', num_cards_to_draw, player_id)
            elif num_cards_to_draw < 0:
                num_cards_to_discard = min(-num_cards_to_draw, player.number_cards_in_hand())
                new_actions = []
                for _ in range(num_cards_to_discard):
                    new_actions.append({'player_id': player_id, 'name': 'Discard', 'view_mode': 'View Hand',
                                        'view_id': player_id, 'color': None})
                self.action_queue = new_actions + self.action_queue
            self.update_game()

        start_new_turn = False
        player.stabilized = False
        self.active_player += 1
        if self.active_player == self.num_players:
            start_new_turn = True
            self.turn += 1
            self.active_player = 0

        self.players[self.active_player].number_cards_turn = 1
        self.update_game()
        if start_new_turn:
            self.start_new_turn()
        self.update_game()

    def start_new_turn(self):
        self.turn_restrictions = []
        self.end_turn_number_cards = None
        self.ignore_actions = False
        active_age = self.ages_pile[0]
        del self.ages_pile[0]
        self.eras[self.current_era].append(active_age)

        self.update_game()
        if type(active_age).__name__ == 'Catastrophe':
            self.current_era += 1

            self.modify_gene_pool(affected_players='all', value=active_age.gene_pool_effect)

            for effect in active_age.catastrophe_effects:
                function_name = effect['name']
                params = effect['params']
                game_function = getattr(self, function_name)
                game_function(**params)
                self.update_game()

            if self.current_era == self.num_eras:
                self.world_ended = True
                self.world_end_effect = False
                self.update_game()

        else:
            for effect in active_age.instant_effects:
                function_name = effect['name']
                params = effect['params']
                game_function = getattr(self, function_name)
                game_function(**params)
                self.update_game()

            for effect in active_age.turn_effects:
                function_name = effect['name']
                params = effect['params']
                game_function = getattr(self, function_name)
                game_function(**params)
                self.update_game()

    def world_end(self):

        '''for player_id, player in enumerate(self.players):
            self.resolve_world_end_traits(player_id)
            self.update_game()'''
        if not self.world_end_effect:
            self.resolve_world_end_effect()
            self.world_end_effect = True
        if len(self.action_queue) > 0:
            self.update_game()
            return

        if not self.scored_compiled:
            self.compile_score()

        self.game_state = ['End game' for _ in range(self.num_players)]

    def resolve_world_end_traits(self, player_id):
        pass

    def resolve_world_end_effect(self):
        if not self.world_end_effect:
            last_catastrophe = self.eras[self.num_eras - 1][-1]

            effect = last_catastrophe.world_end_effect
            function_name = effect['name']
            params = effect['params']
            game_function = getattr(self, function_name)
            game_function(**params)

            self.world_end_effect = True

    def compile_score(self):

        for player_id, player in enumerate(self.players):
            # world end points
            self.scores[player_id]['world_end'] = player.world_end_points

            # face value points
            for color, cards in player.trait_pile.items():
                for card in cards:
                    if card.face_value is not None:
                        self.scores[player_id]['face_values'] += card.face_value

            # bonus points
            for traits in player.trait_pile.values():
                for trait in traits:
                    if trait.bonus_points is not None and not trait.bonus_counted:
                        bonus_point_function = trait.bonus_points
                        function_name = bonus_point_function['name']
                        params = bonus_point_function['params']
                        game_function = getattr(self, function_name)
                        game_function(player_id, **params)
                        trait.bonus_counted = True

            self.scores[player_id]['bonus_points'] = player.bonus_points

        self.scored_compiled = True

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
                        elif not self.play_condition_met(player_id, card):
                            card.playable = False
                        elif card.is_dominant and player.number_dominants >= 2:
                            card.playable = False
                        elif self.action_queue and self.action_queue[0]['name'] in ['Discard', 'Random Discard']:
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
        elif num_cards_to_draw < 0:
            num_cards_to_discard = min(-num_cards_to_draw, player.number_cards_in_hand())
            new_actions = []
            for _ in range(num_cards_to_discard):
                new_actions.append({'player_id': player_id, 'name': 'Discard', 'view_mode': 'View Hand',
                                    'view_id': player_id, 'color': None})
            self.action_queue = new_actions + self.action_queue
        self.update_game()
        player.number_cards_turn = 0
        self.update_game()

    def stabilize_all_players(self, reset_stabilize):
        for player_id in range(self.num_players):
            self.stabilize(player_id)
            if reset_stabilize:
                self.players[player_id].stabilized = False

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

    def update_selection(self, player_id, view_mode, view_id, selected_index, color=None):
        player = self.players[player_id]
        if view_mode == 'View Hand':
            if {'view_id': view_id, 'card_index': selected_index} in player.current_selection[view_mode]:
                player.current_selection[view_mode].remove({'view_id': view_id, 'card_index': selected_index})
            else:
                player.current_selection[view_mode].append({'view_id': view_id, 'card_index': selected_index})
        if view_mode == 'View Trait Piles':
            if {'view_id': view_id, 'color': color, 'card_index': selected_index} in player.current_selection[view_mode]:
                player.current_selection[view_mode].remove({'view_id': view_id, 'color': color, 'card_index': selected_index})
            else:
                player.current_selection[view_mode].append({'view_id': view_id, 'color': color, 'card_index': selected_index})
        self.update_game()

    def discard_selected_card(self, player_id):
        player = self.players[player_id]
        action = self.action_queue[0]
        action_view_mode = action['view_mode']
        action_view_id = action['view_id']
        action_color = action['color']
        current_player_selection = player.current_selection
        if action_color is None:
            action_selection = [selected_card for selected_card in current_player_selection[action_view_mode]
                                if selected_card['view_id'] == action_view_id][0]
        else:
            action_selection = [selected_card for selected_card in current_player_selection[action_view_mode]
                                if selected_card['view_id'] == action_view_id and selected_card['color'] == action_color]
        selected_index = action_selection['card_index']
        del self.action_queue[0]
        if action_view_mode == 'View Hand':
            discarded_card = self.players[action_view_id].hand[selected_index]
            del self.players[action_view_id].hand[selected_index]
        elif action_view_mode == 'View Trait Piles':
            selected_color = action_selection['color']
            discarded_card = self.players[action_view_id].trait_pile[selected_color][selected_index]
            if discarded_card.remove_effects is not None:
                for effect in discarded_card.remove_effects:
                    function_name = effect['name']
                    params = effect['params']
                    game_function = getattr(self, function_name)
                    game_function(**params)
                    self.update_game()
            del self.players[action_view_id].trait_pile[selected_color][selected_index]
        self.discard_pile.append(discarded_card)
        self.last_discarded_card = discarded_card
        self.last_discard_player_id = player_id
        self.reset_selections(player_id)
        self.update_game()

    def discard_random_card(self, player_id):
        player = self.players[player_id]
        action = self.action_queue[0]
        action_view_mode = action['view_mode']
        action_view_id = action['view_id']
        action_color = action['color']
        del self.action_queue[0]
        random_index = random.randint(0, player.number_cards_in_hand() - 1)
        discarded_card = self.players[action_view_id].hand[random_index]
        del self.players[action_view_id].hand[random_index]
        self.discard_pile.append(discarded_card)
        self.last_discarded_card = discarded_card
        self.last_discard_player_id = player_id
        self.reset_selections(player_id)
        self.update_game()

    def add_turn_restriction(self, restricted_attribute, restricted_value, restricted_type):
        self.turn_restrictions.append({'restricted_attribute': restricted_attribute,
                                       'restricted_value': restricted_value,
                                       'restricted_type': restricted_type})

    def turn_ignore_actions(self):
        self.ignore_actions = True

    def add_cards_to_discard_from_hand(self, affected_players, value):
        if affected_players == 'all':
            new_actions = []
            for player_id, player in enumerate(self.players):
                num_cards_to_discard = min(value, player.number_cards_in_hand())
                for _ in range(num_cards_to_discard):
                    new_actions.append({'player_id': player_id, 'name': 'Discard', 'view_mode': 'View Hand',
                                        'view_id': player_id, 'color': None})
            self.action_queue = new_actions + self.action_queue

    def turn_restricted(self, card):
        for restriction in self.turn_restrictions:
            restricted_attribute_value = getattr(card, restriction['restricted_attribute'])
            if restricted_attribute_value is None:
                return False
            if restriction['restricted_type'] == 'equal':
                if restricted_attribute_value == restriction['restricted_value']:
                    return True
            elif restriction['restricted_type'] == 'greater_than':
                if restricted_attribute_value > restriction['restricted_value']:
                    return True
            elif restriction['restricted_type'] == 'smaller_than':
                if restricted_attribute_value < restriction['restricted_value']:
                    return True
        return False

    def play_condition_met(self, player_id, card):
        player = self.players[player_id]
        if card.play_conditions is None:
            return True
        else:
            for condition in card.play_conditions:
                function_name = condition['name']
                params = condition['params']
                game_function = getattr(player, function_name)
                if not game_function(**params):
                    return False
        return True

    def modify_number_cards_turn(self, affected_players, value):
        if affected_players == 'all':
            for player in self.players:
                player.number_cards_turn = value

    def discard_card_from_hand(self, affected_players, num_cards, player_id=None, random_discard=False):
        if affected_players == 'self':
            player = self.players[player_id]
            new_actions = []
            num_cards_to_discard = min(player.number_cards_in_hand(), num_cards)
            for _ in range(num_cards_to_discard):
                if random_discard:
                    new_actions.append({'player_id': player_id, 'name': 'Random Discard', 'view_mode': 'View Hand',
                                        'view_id': player_id, 'color': None})
                else:
                    new_actions.append({'player_id': player_id, 'name': 'Discard', 'view_mode': 'View Hand',
                                        'view_id': player_id, 'color': None})
            self.action_queue = new_actions + self.action_queue
        elif affected_players == 'opponents':
            for p_id, player in enumerate(self.players):
                if p_id != player_id:
                    new_actions = []
                    num_cards_to_discard = min(player.number_cards_in_hand(), num_cards)
                    for _ in range(num_cards_to_discard):
                        if random_discard:
                            new_actions.append(
                                {'player_id': p_id, 'name': 'Random Discard', 'view_mode': 'View Hand',
                                 'view_id': p_id, 'color': None})
                        else:
                            new_actions.append({'player_id': p_id, 'name': 'Discard', 'view_mode': 'View Hand',
                                                'view_id': p_id, 'color': None})
                    self.action_queue = new_actions + self.action_queue
        elif affected_players == 'all':
            for p_id, player in enumerate(self.players):
                new_actions = []
                num_cards_to_discard = min(player.number_cards_in_hand(), num_cards)
                for _ in range(num_cards_to_discard):
                    if random_discard:
                        new_actions.append(
                            {'player_id': p_id, 'name': 'Random Discard', 'view_mode': 'View Hand',
                             'view_id': p_id, 'color': None})
                    else:
                        new_actions.append({'player_id': p_id, 'name': 'Discard', 'view_mode': 'View Hand',
                                            'view_id': p_id, 'color': None})
                self.action_queue = new_actions + self.action_queue

    def discard_card_from_trait_pile(self, affected_players, num_cards, color=None, player_id=None):
        if affected_players == 'opponents':
            for p_id, player in enumerate(self.players):
                if p_id != player_id:
                    new_actions = []
                    num_cards_to_discard = min(player.number_traits(color), num_cards)
                    for _ in range(num_cards_to_discard):
                        new_actions.append({'player_id': p_id, 'name': 'Discard', 'view_mode': 'View Trait Piles',
                                            'view_id': p_id, 'color': color})
                    self.action_queue = new_actions + self.action_queue
        if affected_players == 'self':
            player = self.players[player_id]
            new_actions = []
            num_cards_to_discard = min(player.number_traits(color), num_cards)
            for _ in range(num_cards_to_discard):
                new_actions.append({'player_id': player_id, 'name': 'Discard', 'view_mode': 'View Trait Piles',
                                    'view_id': player_id, 'color': color})
            self.action_queue = new_actions + self.action_queue
        if affected_players == 'all':
            new_actions = []
            for p_id, player in enumerate(self.players):
                num_traits_to_discard = min(player.number_traits(color), num_cards)
                for _ in range(num_traits_to_discard):
                    new_actions.append({'player_id': p_id, 'name': 'Discard',
                                        'view_mode': 'View Trait Piles', 'view_id': p_id, 'color': color})
            self.action_queue = new_actions + self.action_queue

    def discard_hand(self, affected_players, player_id=None):
        if affected_players == 'self':
            player = self.players[player_id]
            discarded_cards = player.hand
            self.discard_pile += discarded_cards
            player.hand = []
            self.last_discarded_card = discarded_cards[-1]
            self.last_discard_player_id = player_id
            self.reset_selections(player_id)
            self.update_game()

    def skip_stabilization(self, affected_players, player_id=None):
        if affected_players == 'self':
            self.players[player_id].stabilized = True

    def draw_card_for_every_color_type(self, affected_players):
        if affected_players == 'all':
            for player_id, player in enumerate(self.players):
                num_cards_to_draw = player.number_colors('trait_pile')
                self.draw_cards('self', num_cards_to_draw, player_id=player_id)

    def discard_card_from_hand_for_every_color(self, affected_players, color):
        if affected_players == 'all':
            new_actions = []
            for player_id, player in enumerate(self.players):
                num_cards_to_discard = min(player.number_traits(color), player.number_cards_in_hand())
                for _ in range(num_cards_to_discard):
                    new_actions.append({'player_id': player_id, 'name': 'Discard', 'view_mode': 'View Hand',
                                        'view_id': player_id, 'color': None})
            self.action_queue = new_actions + self.action_queue

    def discard_card_from_hand_for_every_dominant(self, affected_players):
        if affected_players == 'all':
            new_actions = []
            for player_id, player in enumerate(self.players):
                num_cards_to_discard = min(player.number_dominants, player.number_cards_in_hand())
                for _ in range(num_cards_to_discard):
                    new_actions.append({'player_id': player_id, 'name': 'Discard', 'view_mode': 'View Hand',
                                        'view_id': player_id, 'color': None})
            self.action_queue = new_actions + self.action_queue

    def play_another_trait(self, affected_players, num_traits, player_id=None, ignore_actions=False):
        if affected_players == 'self':
            player = self.players[player_id]
            player.number_cards_turn += num_traits
            new_actions = []
            for _ in range(num_traits):
                new_actions.append({'player_id': player_id, 'name': 'Play Card',
                                    'view_mode': 'View Hand', 'view_id': player_id, 'color': None,
                                    'ignore_actions': ignore_actions})
            self.action_queue = new_actions + self.action_queue

    def set_end_turn_number_cards(self, num_cards):
        self.end_turn_number_cards = num_cards

    def play_heroic(self):
        for player_id, player in enumerate(self.players):
            card_indexes = []
            for card_index, card in enumerate(player.hand):
                if card.name == 'Heroic':
                    card_indexes.append(card_index)
            card_indexes.reverse()
            for card_index in card_indexes:
                player.number_cards_turn += 1
                self.reset_selections(player_id)
                player.current_selection['View Hand'].append({'view_id': player_id, 'card_index': card_index})
                self.play_selected_card(player_id, player_id)

    def modify_world_end_points_for_every_color(self, affected_players, color, value):
        if affected_players == 'all':
            for player in self.players:
                number_traits_color = player.number_traits(color)
                player.world_end_points += number_traits_color * value

    def modify_world_end_points_fewest_traits(self, affected_players, value):
        if affected_players == 'all':
            min_traits = min([player.number_traits() for player in self.players])
            for player in self.players:
                if player.number_traits() == min_traits:
                    player.world_end_points += value

    def modify_world_end_points_face_value(self, affected_players, face_value, compare_type, value):
        if affected_players == 'all':
            for player in self.players:
                if compare_type == 'greater_than':
                    number_traits = player.number_traits_above(face_value)
                player.world_end_points += number_traits * value

    def bonus_kidney(self, player_id):
        player = self.players[player_id]
        player.bonus_points += player.number_kidneys()

    def bonus_swarm(self, player_id):
        player = self.players[player_id]
        player.bonus_points += sum([player.number_swarms() for player in self.players])

    def bonus_for_every_color(self, player_id, color, value):
        player = self.players[player_id]
        player.bonus_points += player.number_traits(color=color) * value

    def bonus_gene_pool(self, player_id):
        player = self.players[player_id]
        player.bonus_points += player.gene_pool

    def bonus_max_gene_pool(self, player_id):
        player = self.players[player_id]
        player.bonus_points += max([player.gene_pool for player in self.players])

    def bonus_number_cards_hand(self, player_id, card_type='all'):
        player = self.players[player_id]
        player.bonus_points += player.number_cards_in_hand(card_type)

    def bonus_all_colors_trait_pile(self, player_id, value):
        player = self.players[player_id]
        if player.number_colors('trait_pile') == 4:
            player.bonus_points += value

    def bonus_number_colors(self, player_id, location, value):
        player = self.players[player_id]
        player.bonus_points += player.number_colors(location) * value

    def bonus_more_traits(self, player_id, value):
        player = self.players[player_id]
        players_num_traits = sorted([player.number_traits() for player in self.players], reverse=True)

        if player.number_traits() == players_num_traits[0] and players_num_traits[0] > players_num_traits[1]:
            player.bonus_points += value

    def bonus_discard_expansion(self, player_id, expansion, value):
        player = self.players[player_id]
        for card in self.discard_pile:
            if card.expansion == expansion:
                player.bonus_points += value

    def bonus_discard_dominant(self, player_id, value):
        player = self.players[player_id]
        for card in self.discard_pile:
            if card.is_dominant:
                player.bonus_points += value

    def bonus_negative_face_value(self, player_id, value):
        player = self.players[player_id]
        player.bonus_points += player.number_traits_negative() * value

    def bonus_number_traits(self, player_id, value):
        player = self.players[player_id]
        player.bonus_points += player.number_traits() * value

    def bonus_lowest_color(self, player_id, value):
        player = self.players[player_id]
        if player.number_colors('trait_pile') >= 2:
            player.bonus_points += player.lowest_color_count() * value

    def bonus_every_negative_discard(self, player_id, every, value):
        player = self.players[player_id]
        number_negative = 0
        for card in self.discard_pile:
            if card.face_value is not None and card.face_value < 0:
                number_negative += 1
        player.bonus_points += int(number_negative / every) * value

    def bonus_dominant_hand(self, player_id, value):
        player = self.players[player_id]
        player.bonus_points += player.number_cards_in_hand(card_type='dominant') * value

    def bonus_expansion_all_trait_piles(self, player_id, expansion, value):
        player = self.players[player_id]
        player.bonus_points += sum([player.number_traits_expansion(expansion) for player in self.players]) * value

    def bonus_face_value(self, player_id, face_value, value):
        player = self.players[player_id]
        player.bonus_points += player.number_traits_equal(face_value) * value

    def bonus_color_pair_opponents(self, player_id, color, value):
        player = self.players[player_id]
        number_color_pairs = [int(player.number_traits(color) / 2) for p_id, player in enumerate(self.players) if p_id != player_id]
        player.bonus_points += sum(number_color_pairs) * value

    def bonus_color_pair(self, player_id, value):
        player = self.players[player_id]
        color_pairs = [int(player.number_traits(color) / 2) for color in player.trait_pile_colors if color != 'Colorless']
        player.bonus_points += sum(color_pairs) * value

    def update_buttons(self):
        num_queued_actions = len(self.action_queue)
        if num_queued_actions > 0:
            current_action = self.action_queue[0]
        else:
            current_action = None
        for player_id, player in enumerate(self.players):
            player_buttons = []
            if player_id == self.active_player and num_queued_actions == 0:
                player_buttons = []
                if player.stabilized:
                    player_buttons.append('End Turn')
                else:
                    player_buttons.append('Stabilize')
            selected_card_indexes = [selected_card for selected_card in player.current_selection['View Hand'] if selected_card['view_id'] == player_id]
            if len(selected_card_indexes) == 1:
                selected_card_index = selected_card_indexes[0]['card_index']
                if player.hand[selected_card_index].playable:
                    player_buttons.append('Play Card')
            if current_action is not None:
                if self.action_doable(current_action, player_id):
                    player_buttons.append(current_action['name'])
            self.active_buttons[player_id] = player_buttons

    def action_doable(self, action, player_id):
        action_view_mode = action['view_mode']
        action_view_id = action['view_id']
        action_color = action['color']
        if action['name'] == 'Random Discard':
            if player_id == action['view_id']:
                return True
            else:
                return False
        player = self.players[player_id]
        current_player_selection = player.current_selection
        if not current_player_selection[action_view_mode]:
            return False
        if action_color is None:
            action_selection = [selected_card for selected_card in current_player_selection[action_view_mode]
                                if selected_card['view_id'] == action_view_id]
        else:
            action_selection = [selected_card for selected_card in current_player_selection[action_view_mode]
                                if selected_card['view_id'] == action_view_id and selected_card['color'] == action_color]
        if len(action_selection) == 1:
            return True
        else:
            return False

    def update_action_queue(self):
        while len(self.action_queue) > 0:
            current_action = self.action_queue[0]
            if current_action['name'] == 'Discard':
                if current_action['view_mode'] == 'View Hand':
                    if self.players[current_action['view_id']].number_cards_in_hand() == 0:
                        del self.action_queue[0]
                    else:
                        break
                elif current_action['view_mode'] == 'View Trait Piles':
                    if self.players[current_action['view_id']].number_traits(current_action['color']) == 0:
                        del self.action_queue[0]
                    else:
                        break
            elif current_action['name'] == 'Random Discard':
                if current_action['view_mode'] == 'View Hand':
                    if self.players[current_action['view_id']].number_cards_in_hand() == 0:
                        del self.action_queue[0]
                    else:
                        break
            elif current_action['name'] == 'Play Card':
                if current_action['view_mode'] == 'View Hand':
                    if self.players[current_action['view_id']].number_cards_playable() == 0:
                        del self.action_queue[0]
                    else:
                        break

    def update_game_state(self):
        if len(self.action_queue) > 0:
            current_action = self.action_queue[0]
            action_player_id = current_action['player_id']
            action_name = current_action['name']
            for player_id, player in enumerate(self.players):
                if player_id == action_player_id:
                    self.game_state[player_id] = action_name
                else:
                    self.game_state[player_id] = 'Waiting for Players Actions'
        elif self.world_ended:
            self.world_end()
        else:
            for player_id, player in enumerate(self.players):
                self.game_state[player_id] = 'Playing'

    def update_game(self):
        self.update_action_queue()
        self.update_game_state()
        self.hand_playable()
        self.update_buttons()
        self.selections_check()

    def update_view_id(self, player_id, view_mode, value):
        self.players[player_id].view_modes[view_mode] += value

    def reset_selections(self, player_id):
        player = self.players[player_id]
        player.current_selection = {'View Hand': [],
                                    'View Trait Piles': []}

    def selections_check(self):
        for player_id, player in enumerate(self.players):
            for view_mode, selected_indexes in player.current_selection.items():
                if view_mode == 'View Hand':
                    for selected_index in selected_indexes:
                        selection_view_id = selected_index['view_id']
                        selection_card_index = selected_index['card_index']
                        if selection_card_index >= self.players[selection_view_id].number_cards_in_hand():
                            player.current_selection[view_mode].remove(selected_index)
                if view_mode == 'View Trait Piles':
                    for selected_index in selected_indexes:
                        selection_view_id = selected_index['view_id']
                        selection_color = selected_index['color']
                        selection_card_index = selected_index['card_index']
                        if selection_card_index >= self.players[selection_view_id].number_traits(selection_color):
                            player.current_selection[view_mode].remove(selected_index)

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
        for player_id in range(self.num_players):
            cards_playable = [card.playable for card in self.players[player_id].hand]
            displayed_text += str(cards_playable)

        return displayed_text
