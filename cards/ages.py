import os


class Age:

    def __init__(self, name, turn_effects, instant_effects, expansion,
                 images_folder=os.path.join(r'C:\Users\fireb\Projects\Doomlings\cards\images')):
        self.name = name
        self.turn_effects = turn_effects
        self.instant_effects = instant_effects
        self.expansion = expansion
        self.img_path = os.path.join(images_folder, f'{self.name}.png')


birth_of_life = Age(name='The Birth of Life', turn_effects=[],
                    instant_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'all', 'value': 5}},
                                     {'name': 'stabilize_all_players', 'params': {'reset_stabilize': True}},
                                     {'name': 'modify_number_cards_turn',
                                      'params': {'affected_players': 'all', 'value': 1}}],
                    expansion='Base')

ages = [Age(name='Tropical Lands',
            turn_effects=[{'name': 'add_turn_restriction', 'params': {'restricted_attribute': 'color',
                                                                      'restricted_value': 'Colorless',
                                                                      'restricted_type': 'equal'}}],
            instant_effects=[], expansion='Base'),
        Age(name='Arid Lands',
            turn_effects=[{'name': 'add_turn_restriction', 'params': {'restricted_attribute': 'color',
                                                                      'restricted_value': 'Blue',
                                                                      'restricted_type': 'equal'}}],
            instant_effects=[], expansion='Base'),
        Age(name='Tectonic Shift',
            turn_effects=[{'name': 'add_turn_restriction', 'params': {'restricted_attribute': 'color',
                                                                      'restricted_value': 'Green',
                                                                      'restricted_type': 'equal'}}],
            instant_effects=[], expansion='Base'),
        Age(name='Eclipse',
            turn_effects=[{'name': 'add_turn_restriction', 'params': {'restricted_attribute': 'color',
                                                                      'restricted_value': 'Red',
                                                                      'restricted_type': 'equal'}}],
            instant_effects=[], expansion='Base'),
        Age(name='Lunar Retreat',
            turn_effects=[{'name': 'add_turn_restriction', 'params': {'restricted_attribute': 'color',
                                                                      'restricted_value': 'Purple',
                                                                      'restricted_type': 'equal'}}],
            instant_effects=[], expansion='Base'),
        Age(name='Glacial Drift',
            turn_effects=[{'name': 'add_turn_restriction', 'params': {'restricted_attribute': 'face_value',
                                                                      'restricted_value': 3,
                                                                      'restricted_type': 'greater_than'}}],
            instant_effects=[], expansion='Base'),
        Age(name='Flourish', turn_effects=[],
            instant_effects=[{'name': 'draw_cards', 'params': {'affected_players': 'all', 'value': 2}}],
            expansion='Base')
        ] + [Age(name='Northern Winds', turn_effects=[],
                 instant_effects=[{'name': 'draw_cards', 'params': {'affected_players': 'all', 'value': 1}},
                                  {'name': 'modify_number_cards_to_discard',
                                   'params': {'affected_players': 'all', 'value': 1}}],
                 expansion='Base') for _ in range(2)]

"""ages = [Age(name='Northern Winds', turn_effects=[],
            instant_effects=[{'name': 'draw_cards', 'params': {'affected_players': 'all', 'value': 1}},
                             {'name': 'modify_number_cards_to_discard', 'params': {'affected_players': 'all', 'value': 1}}],
            expansion='Base') for _ in range(20)]"""
