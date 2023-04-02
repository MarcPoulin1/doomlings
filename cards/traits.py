import os


class Trait:

    def __init__(self, name, face_value, color, effects=None, remove_effects=None, actions=None, bonus_points=None,
                 expansion='Base', is_dominant=False, bonus_counted=False, playable=False):
        self.name = name
        self.face_value = face_value
        self.color = color
        self.effects = effects
        self.remove_effects = remove_effects
        self.actions = actions
        self.bonus_points = bonus_points
        self.expansion = expansion
        self.is_dominant = is_dominant
        self.bonus_counted = bonus_counted
        self.playable = playable


traits = [Trait(name='Talons', face_value=2, color='Purple', expansion='Dinolings'),
          Trait(name='Bark', face_value=2, color='Green'),
          Trait(name='Migratory', face_value=2, color='Blue'),
          Trait(name='Stone Skin', face_value=2, color='Red'),
          Trait(name='Destined', face_value=4, color='Colorless', expansion='Mythlings'),
          Trait(name='Saliva',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=1, color='Blue'),
          Trait(name='Teeth',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=1, color='Purple'),
          Trait(name='Dreamer',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=1, color='Purple'),
          Trait(name='Brute Strength',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                face_value=4, color='Red'),
          Trait(name='Mitochondrion',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=1, color='Colorless'),
          Trait(name='Super Spreader',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'all', 'value': -1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'all', 'value': 1}}],
                face_value=2, color='Purple'),
          Trait(name='Just',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=2, color='Colorless'),
          Trait(name='Warm Blood',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 2}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -2}}],
                face_value=-1, color='Red'),
          Trait(name='Fecundity',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=1, color='Green'),
          Trait(name='Ceratopsian Horns', face_value=4, color='Green',
                expansion='Dinolings'),
          Trait(name='Big Ears', face_value=1, color='Purple'),
          Trait(name='Woody Stems', face_value=1, color='Green'),
          Trait(name='Antlers', face_value=3, color='Red'),
          Trait(name='Gills', face_value=1, color='Blue'),
          Trait(name='Fire Skin', face_value=3, color='Red'),
          Trait(name='Icy', face_value=3, color='Blue', expansion='Mythlings'),
          Trait(name='Blubber', face_value=4, color='Blue'),
          Trait(name='Quick', face_value=2, color='Red'),
          Trait(name='Diaphanous Wings', face_value=-1, color='Blue',
                expansion='Mythlings'),
          Trait(name='Confusion', face_value=-2, color='Colorless'),
          Trait(name='Spiny', face_value=1, color='Blue'),
          Trait(name='Leaves', face_value=1, color='Green'),
          Trait(name='Fine Motor Skills', face_value=2, color='Purple'),
          Trait(name='Fear', face_value=1, color='Colorless'),
          Trait(name='Nocturnal', face_value=3, color='Purple'),
          Trait(name='Adorable', face_value=4, color='Purple'),
          Trait(name='Fangs', face_value=1, color='Red'),
          Trait(name='Appealing', face_value=3, color='Green'),
          Trait(name='Deep Roots', face_value=2, color='Green'),
          Trait(name='Flatulence', face_value=3, color='Colorless'),
          Trait(name='Indomitable', is_dominant=True,
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -2}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 2}}],
                face_value=10, color='Red'),
          Trait(name='Legendary', is_dominant=True,
                effects=[{'name': 'discard_hand', 'params': {'affected_players': 'self'}},
                         {'name': 'skip_stabilization', 'params': {'affected_players': 'self'}}], face_value=8,
                color='Blue'),
          Trait(name='Kidney Chefs Toque',
                bonus_points={'name': 'bonus_kidney', 'params': {}}, face_value=None, color='Red'),
          Trait(name='Kidney Combover',
                bonus_points={'name': 'bonus_kidney', 'params': {}}, face_value=None, color='Red'),
          Trait(name='Kidney Elf Hat',
                bonus_points={'name': 'bonus_kidney', 'params': {}}, face_value=None, color='Red'),
          Trait(name='Kidney Party Hat',
                bonus_points={'name': 'bonus_kidney', 'params': {}}, face_value=None, color='Red'),
          Trait(name='Kidney Tiara',
                bonus_points={'name': 'bonus_kidney', 'params': {}}, face_value=None, color='Red'),
          Trait(name='Kidney Topper',
                bonus_points={'name': 'bonus_kidney', 'params': {}}, face_value=None, color='Red'),
          Trait(name='Swarm Fur',
                bonus_points={'name': 'bonus_swarm', 'params': {}}, face_value=None, color='Green'),
          Trait(name='Swarm Horns',
                bonus_points={'name': 'bonus_swarm', 'params': {}}, face_value=None, color='Green'),
          Trait(name='Swarm Mindless',
                bonus_points={'name': 'bonus_swarm', 'params': {}}, face_value=None, color='Green'),
          Trait(name='Swarm Spots',
                bonus_points={'name': 'bonus_swarm', 'params': {}}, face_value=None, color='Green'),
          Trait(name='Swarm Stripes',
                bonus_points={'name': 'bonus_swarm', 'params': {}}, face_value=None, color='Green'),
          Trait(name='Heat Vision',
                bonus_points={'name': 'bonus_for_every_color', 'params': {'color': 'Red', 'value': 1}},
                face_value=-1, color='Red'),
          Trait(name='Sticky Secretions',
                bonus_points={'name': 'bonus_for_every_color', 'params': {'color': 'Purple', 'value': 1}},
                face_value=-1, color='Purple'),
          Trait(name='Egg Clusters',
                bonus_points={'name': 'bonus_for_every_color', 'params': {'color': 'Blue', 'value': 1}},
                face_value=-1, color='Blue'),
          Trait(name='Overgrowth',
                bonus_points={'name': 'bonus_for_every_color', 'params': {'color': 'Green', 'value': 1}},
                face_value=-1, color='Green'),
          Trait(name='Mindful',
                bonus_points={'name': 'bonus_for_every_color', 'params': {'color': 'Colorless', 'value': 1}},
                face_value=-1, color='Colorless'),
          Trait(name='Random Fertilization',
                bonus_points={'name': 'bonus_gene_pool', 'params': {}},
                face_value=None, color='Green'),
          Trait(name='Altruistic',
                bonus_points={'name': 'bonus_gene_pool', 'params': {}},
                face_value=None, color='Colorless'),
          Trait(name='Hyper-Myelination',
                bonus_points={'name': 'bonus_max_gene_pool', 'params': {}},
                face_value=None, color='Purple',
                expansion='Techlings'),
          Trait(name='Fortunate',
                bonus_points={'name': 'bonus_number_cards_hand', 'params': {}},
                face_value=None, color='Green'),
          Trait(name='Boredom',
                bonus_points={'name': 'bonus_number_cards_hand', 'params': {'card_type': 'effect'}},
                face_value=None, color='Colorless'),
          Trait(name='Dragon Heart',
                bonus_points={'name': 'bonus_all_colors_trait_pile', 'params': {'value': 4}},
                face_value=1, color='Red',
                expansion='Mythlings'),
          Trait(name='Gratitude',
                bonus_points={'name': 'bonus_number_colors', 'params': {'location': 'trait_pile', 'value': 1}},
                face_value=None, color='Colorless'),
          Trait(name='Saudade',
                bonus_points={'name': 'bonus_number_colors', 'params': {'location': 'hand', 'value': 1}},
                face_value=1, color='Colorless'),
          Trait(name='Apex Predator',
                bonus_points={'name': 'bonus_more_traits', 'params': {'value': 4}},
                face_value=4, color='Red', is_dominant=True),
          Trait(name='Camouflage',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                bonus_points={'name': 'bonus_number_cards_hand', 'params': {}},
                face_value=1, color='Purple', is_dominant=True),
          Trait(name='Immunity',
                bonus_points={'name': 'bonus_negative_face_value', 'params': {'value': 2}},
                face_value=4, color='Blue', is_dominant=True),
          Trait(name='Tiny',
                bonus_points={'name': 'bonus_number_traits', 'params': {'value': -1}},
                face_value=17, color='Blue', is_dominant=True),
          Trait(name='Tiny Arms',
                bonus_points={'name': 'bonus_discard_expansion', 'params': {'expansion': 'Dinolings', 'value': 1}},
                face_value=-1, color='Red', expansion='Dinolings'),
          Trait(name='Serrated Teeth',
                bonus_points={'name': 'bonus_discard_dominant', 'params': {'value': 1}},
                face_value=-1, color='Red', expansion='Dinolings'),
          Trait(name='Symbiosis',
                bonus_points={'name': 'bonus_lowest_color', 'params': {'value': 2}},
                face_value=3, color='Green', is_dominant=True),
          Trait(name='Cranial Crest',
                bonus_points={'name': 'bonus_every_negative_discard', 'params': {'every': 3, 'value': 1}},
                face_value=1, color='Colorless',
                expansion='Dinolings'),
          Trait(name='Brave',
                bonus_points={'name': 'bonus_dominant_hand', 'params': {'value': 2}},
                face_value=1, color='Red'),
          Trait(name='Elven Ears',
                bonus_points={'name': 'bonus_expansion_all_trait_piles',
                              'params': {'expansion': 'Mythlings', 'value': 1}},
                face_value=-1, color='Green', expansion='Mythlings'),
          Trait(name='Pollination',
                bonus_points={'name': 'bonus_face_value', 'params': {'face_value': 1, 'value': 1}},
                face_value=1, color='Green'),
          Trait(name='Branches',
                bonus_points={'name': 'bonus_color_pair_opponents', 'params': {'color': 'Green', 'value': 1}},
                face_value=0, color='Green'),
          Trait(name='Pack Behavior',
                bonus_points={'name': 'bonus_color_pair', 'params': {'value': 1}},
                face_value=3, color='Green', is_dominant=True),
          Trait(name='Sweat',
                actions=[{'name': 'discard_card_from_hand', 'params': {'affected_players': 'self', 'num_cards': 1}}],
                face_value=2,
                color='Blue'),
          Trait(name='Hot Temper',
                actions=[{'name': 'discard_card_from_hand', 'params': {'affected_players': 'self', 'num_cards': 2}}],
                face_value=2,
                color='Red'),
          Trait(name='Territorial',
                actions=[{'name': 'discard_card_from_trait_pile',
                          'params': {'affected_players': 'opponents', 'num_cards': 1, 'color': 'Red'}}],
                face_value=1,
                color='Red'),
          Trait(name='Bad',
                actions=[{'name': 'discard_card_from_hand',
                          'params': {'affected_players': 'opponents', 'num_cards': 2}}],
                face_value=1,
                color='Red'),
          Trait(name='Introspective',
                actions=[{'name': 'draw_cards',
                          'params': {'affected_players': 'self', 'value': 4}}],
                face_value=1,
                color='Colorless'),
          Trait(name='Introspective',
                actions=[{'name': 'draw_cards',
                          'params': {'affected_players': 'self', 'value': 4}}],
                face_value=1,
                color='Colorless'),
          Trait(name='Iridescent Scales',
                actions=[{'name': 'draw_cards',
                          'params': {'affected_players': 'self', 'value': 3}}],
                face_value=1,
                color='Blue'),
          Trait(name='Propagation',
                actions=[{'name': 'play_another_trait',
                          'params': {'affected_players': 'self', 'num_traits': 1}}],
                face_value=1,
                color='Green')
          ]

traits = [Trait(name='Voracious',
                actions=[{'name': 'discard_card_from_trait_pile',
                          'params': {'affected_players': 'self', 'num_cards': 1}},
                         {'name': 'play_another_trait',
                          'params': {'affected_players': 'self', 'num_traits': 1}}],
                face_value=2,
                color='Red') for _ in range(50)]
