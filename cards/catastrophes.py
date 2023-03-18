import os


class Catastrophe:

    def __init__(self, name, gene_pool_effect, catastrophe_effect, world_end_effect, expansion,
                 images_folder=os.path.join(r'C:\Users\fireb\Projects\Doomlings\cards\images')):
        self.name = name
        self.gene_pool_effect = gene_pool_effect
        self.catastrophe_effect = catastrophe_effect
        self.world_end_effect = world_end_effect
        self.expansion = expansion
        self.img_path = os.path.join(images_folder, f'{self.name}.png')


catastrophes = [Catastrophe(name='Overpopulation', gene_pool_effect=1,
                            catastrophe_effect='Draw 1 card for every color type in your trait pile',
                            world_end_effect='+4 points to the player(s) with the fewest traits in their trait pile',
                            expansion='Base') for i in range(3)]
