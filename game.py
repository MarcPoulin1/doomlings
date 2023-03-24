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
        if card_type == 'effect':
            return sum([1 for card in self.hand if not card.effects])
        elif card_type == 'all':
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

    def number_traits_above(self, face_value):
        number_above = 0
        for traits in self.trait_pile.values():
            for trait in traits:
                if trait.face_value is not None and trait.face_value > face_value:
                    number_above += 1
        return number_above

    def number_kidneys(self):
        kidney_count = 0
        for traits in self.trait_pile.values():
            for trait in traits:
                if trait.name.startswith('Kidney'):
                    kidney_count += 1
        return kidney_count

    def number_swarms(self):
        swarm_count = 0
        for traits in self.trait_pile.values():
            for trait in traits:
                if trait.name.startswith('Swarm'):
                    swarm_count += 1
        return swarm_count


class Game:
    def __init__(self, num_players, age_per_pile=1, num_eras=3, max_gene_pool=8, min_gene_pool=1):
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

    def play_card(self, player_id, trait_pile_id):
        player = self.players[player_id]
        selected_card_index = player.current_selection['View Hand'][0]['card_index']
        played_card = player.hand[selected_card_index]
        self.last_trait_played = played_card
        self.last_player_id = player_id

        self.players[trait_pile_id].trait_pile[played_card.color] += [played_card]
        if played_card.is_dominant:
            player.number_dominants += 1
        del player.hand[selected_card_index]
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

        self.reset_selections(player_id)
        self.update_game()

    def end_turn(self, player_id):
        start_new_turn = False
        self.players[player_id].stabilized = False
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
                    if not trait.bonus_counted:
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
                        elif card.is_dominant and player.number_dominants == 2:
                            card.playable = False
                        elif self.action_queue:
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
            selected_index = action_selection['card_index']
            discarded_card = self.players[action_view_id].hand[selected_index]
            del self.action_queue[0]
            self.discard_pile.append(discarded_card)
            del self.players[action_view_id].hand[selected_index]
        else:
            action_selection = [selected_card for selected_card in current_player_selection[action_view_mode]
                                if selected_card['view_id'] == action_view_id and selected_card['color'] == action_color][0]
            selected_index = action_selection['card_index']
            selected_color = action_selection['color']
            discarded_card = self.players[action_view_id].trait_pile[selected_color][selected_index]
            del self.action_queue[0]
            self.discard_pile.append(discarded_card)
            for effect in discarded_card.remove_effects:
                function_name = effect['name']
                params = effect['params']
                game_function = getattr(self, function_name)
                game_function(**params)
                self.update_game()
            del self.players[action_view_id].trait_pile[selected_color][selected_index]
        self.last_discarded_card = discarded_card
        self.last_discard_player_id = player_id
        self.reset_selections(player_id)
        self.update_game()

    def add_turn_restriction(self, restricted_attribute, restricted_value, restricted_type):
        self.turn_restrictions.append({'restricted_attribute': restricted_attribute,
                                       'restricted_value': restricted_value,
                                       'restricted_type': restricted_type})

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
            self.reset_selections(player_id)
            self.update_game()

    def skip_stabilization(self, affected_players, player_id=None):
        if affected_players == 'self':
            self.players[player_id].stabilized = True

    def draw_card_for_every_color_type(self, affected_players):
        if affected_players == 'all':
            for player_id, player in enumerate(self.players):
                num_cards_to_draw = player.number_colors()
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

    def discard_card_from_trait_pile(self, affected_players, color, value):
        if affected_players == 'all':
            new_actions = []
            for player_id, player in enumerate(self.players):
                num_traits_to_discard = min(player.number_traits(color), value)
                for _ in range(num_traits_to_discard):
                    new_actions.append({'player_id': player_id, 'name': 'Discard',
                                        'view_mode': 'View Trait Piles', 'view_id': player_id, 'color': color})
            self.action_queue = new_actions + self.action_queue

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

    def kidney_bonus(self, player_id):
        player = self.players[player_id]
        player.bonus_points += player.number_kidneys()

    def swarm_bonus(self, player_id):
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
        player = self.players[player_id]
        current_player_selection = player.current_selection
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
        self.compile_score()
        displayed_text += str(self.scores)
        for player_id in range(self.num_players):
            cards_playable = [card.playable for card in self.players[player_id].hand]
            displayed_text += str(cards_playable)

        return displayed_text
