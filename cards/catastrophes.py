import os


class Catastrophe:

    def __init__(self, name, gene_pool_effect, catastrophe_effects, world_end_effect, expansion):
        self.name = name
        self.gene_pool_effect = gene_pool_effect
        self.catastrophe_effects = catastrophe_effects
        self.world_end_effect = world_end_effect
        self.expansion = expansion


catastrophes = [Catastrophe(name='Overpopulation', gene_pool_effect=1,
                            catastrophe_effects=[
                                {'name': 'draw_card_for_every_color_type', 'params': {'affected_players': 'all'}}],
                            world_end_effect='+4 points to the player(s) with the fewest traits in their trait pile',
                            expansion='Base'),
                Catastrophe(name='Ice Age', gene_pool_effect=-1,
                            catastrophe_effects=[
                                {'name': 'discard_card_from_hand_for_every_color', 'params': {'affected_players': 'all', 'color': 'Red'}}],
                            world_end_effect='', expansion='Base'),
                Catastrophe(name='Super Volcano', gene_pool_effect=-1,
                            catastrophe_effects=[
                                {'name': 'discard_card_from_hand_for_every_color', 'params': {'affected_players': 'all', 'color': 'Blue'}}],
                            world_end_effect='', expansion='Base'),
                Catastrophe(name='Mass Extinction', gene_pool_effect=-1,
                            catastrophe_effects=[
                                {'name': 'discard_card_from_hand_for_every_color', 'params': {'affected_players': 'all', 'color': 'Colorless'}}],
                            world_end_effect='', expansion='Base'),
                Catastrophe(name='Retrovirus', gene_pool_effect=-1,
                            catastrophe_effects=[
                                {'name': 'discard_card_from_hand_for_every_color', 'params': {'affected_players': 'all', 'color': 'Green'}}],
                            world_end_effect='', expansion='Base'),
                Catastrophe(name='Impact Event', gene_pool_effect=-1,
                            catastrophe_effects=[
                                {'name': 'discard_card_from_hand_for_every_dominant', 'params': {'affected_players': 'all'}}],
                            world_end_effect='', expansion='Base'),
                Catastrophe(name='Pulse Event', gene_pool_effect=-1,
                            catastrophe_effects=[
                                {'name': 'discard_card_from_hand_for_every_color', 'params': {'affected_players': 'all', 'color': 'Purple'}}],
                            world_end_effect='', expansion='Base')
                ]

catastrophes = [Catastrophe(name='Mass Extinction', gene_pool_effect=-1,
                            catastrophe_effects=[
                                {'name': 'discard_card_from_hand_for_every_color', 'params': {'affected_players': 'all', 'color': 'Colorless'}}],
                            world_end_effect='', expansion='Base') for _ in range(3)]
