import os


class Trait:

    def __init__(self, name, effects, remove_effects, face_value, color, expansion, is_dominant=False,
                 images_folder=os.path.join(r'C:\Users\fireb\Projects\Doomlings\cards\images')):
        self.name = name
        self.effects = effects
        self.remove_effects = remove_effects
        self.face_value = face_value
        self.color = color
        self.expansion = expansion
        self.is_dominant = is_dominant
        self.img_path = os.path.join(images_folder, f'{self.name}.png')


traits = [Trait(name='Talons', effects=[], remove_effects=[], face_value=2, color='Purple', expansion='Dinolings'),
          Trait(name='Bark', effects=[], remove_effects=[], face_value=2, color='Green', expansion='Base'),
          Trait(name='Migratory', effects=[], remove_effects=[], face_value=2, color='Blue', expansion='Base'),
          Trait(name='Stone Skin', effects=[], remove_effects=[], face_value=2, color='Red', expansion='Base'),
          Trait(name='Destined', effects=[], remove_effects=[], face_value=4, color='Colorless', expansion='Mythlings'),
          Trait(name='Saliva',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=1, color='Blue', expansion='Base'),
          Trait(name='Teeth',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=1, color='Purple', expansion='Base'),
          Trait(name='Dreamer',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=1, color='Purple', expansion='Base'),
          Trait(name='Brute Strength',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                face_value=4, color='Red', expansion='Base'),
          Trait(name='Mitochondrion',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=1, color='Colorless', expansion='Base'),
          Trait(name='Super Spreader',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'all', 'value': -1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'all', 'value': 1}}],
                face_value=2, color='Purple', expansion='Base'),
          Trait(name='Just',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=2, color='Colorless', expansion='Base'),
          Trait(name='Warm Blood',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 2}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -2}}],
                face_value=-1, color='Red', expansion='Base'),
          Trait(name='Fecundity',
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 1}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -1}}],
                face_value=1, color='Green', expansion='Base'),
          Trait(name='Ceratopsian Horns', effects=[], remove_effects=[], face_value=4, color='Green',
                expansion='Dinolings'),
          Trait(name='Big Ears', effects=[], remove_effects=[], face_value=1, color='Purple', expansion='Base'),
          Trait(name='Woody Stems', effects=[], remove_effects=[], face_value=1, color='Green', expansion='Base'),
          Trait(name='Antlers', effects=[], remove_effects=[], face_value=3, color='Red', expansion='Base'),
          Trait(name='Gills', effects=[], remove_effects=[], face_value=1, color='Blue', expansion='Base'),
          Trait(name='Fire Skin', effects=[], remove_effects=[], face_value=3, color='Red', expansion='Base'),
          Trait(name='Icy', effects=[], remove_effects=[], face_value=3, color='Blue', expansion='Mythlings'),
          Trait(name='Blubber', effects=[], remove_effects=[], face_value=4, color='Blue', expansion='Base'),
          Trait(name='Quick', effects=[], remove_effects=[], face_value=2, color='Red', expansion='Base'),
          Trait(name='Diaphanous Wings', effects=[], remove_effects=[], face_value=-1, color='Blue',
                expansion='Mythlings'),
          Trait(name='Confusion', effects=[], remove_effects=[], face_value=-2, color='Colorless', expansion='Base'),
          Trait(name='Spiny', effects=[], remove_effects=[], face_value=1, color='Blue', expansion='Base'),
          Trait(name='Leaves', effects=[], remove_effects=[], face_value=1, color='Green', expansion='Base'),
          Trait(name='Fine Motor Skills', effects=[], remove_effects=[], face_value=2, color='Purple',
                expansion='Base'),
          Trait(name='Fear', effects=[], remove_effects=[], face_value=1, color='Colorless', expansion='Base'),
          Trait(name='Nocturnal', effects=[], remove_effects=[], face_value=3, color='Purple', expansion='Base'),
          Trait(name='Adorable', effects=[], remove_effects=[], face_value=4, color='Purple', expansion='Base'),
          Trait(name='Fangs', effects=[], remove_effects=[], face_value=1, color='Red', expansion='Base'),
          Trait(name='Appealing', effects=[], remove_effects=[], face_value=3, color='Green', expansion='Base'),
          Trait(name='Deep Roots', effects=[], remove_effects=[], face_value=2, color='Green', expansion='Base'),
          Trait(name='Flatulence', effects=[], remove_effects=[], face_value=3, color='Colorless', expansion='Base'),
          Trait(name='Indomitable', is_dominant=True,
                effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': -2}}],
                remove_effects=[{'name': 'modify_gene_pool', 'params': {'affected_players': 'self', 'value': 2}}],
                face_value=10, color='Red', expansion='Base'),
          Trait(name='Legendary', is_dominant=True,
                effects=[{'name': 'discard_hand', 'params': {'affected_players': 'self'}},
                         {'name': 'skip_stabilization', 'params': {'affected_players': 'self'}}],
                remove_effects=[],
                face_value=8, color='Blue', expansion='Base')
          ]
