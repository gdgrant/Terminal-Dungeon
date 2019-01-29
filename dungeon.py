### Dungeon class built on top of 2-D maze class
### Author:   gdgrant
### Date:     11/6/2018

import random, copy
from maze import Maze

class Dungeon(Maze):
    """ A 2-D dungeon crawler, including randomized enemies """

    def __init__(self, width, height, exploration):
        """ Build the associated room (maze) based on the given parameters,
            and set up the enemies list """

        Maze.__init__(self, width, height, exploration)
        self.enemies = []
        self.rewards = []


    def cell_state_render(self, i):
        """ An update to the Maze state render, now including enemies (o)
            and an overlap symbol (+) """

        if i == self.current_cell and i in self.enemies:
            state = '+'
            layer = 3
        elif i == self.current_cell:
            state = 'x'
            layer = 3
        elif i in self.enemies:
            state = 'o'
            layer = 2
        elif i == self.cell_ids[-1]:
            state = 'X'
            layer = 3
        elif i in self.rewards:
            state = '*'
            layer = 1
        else:
            state = ' '
            layer = 0
        return state, layer


    def make_enemies(self, num):
        """ Make add new enemies, as many as requested,
            into clear dungeon spaces """
        for n in range(num):
            self.enemies.append(random.choice(list(set(self.cell_ids)-set(self.enemies+[self.current_cell]))))


    def make_rewards(self, num):

        for n in range(num):
            self.rewards.append(random.choice(list(set(self.cell_ids)-set(self.rewards+[self.current_cell, self.cell_list[-1]]))))


    def move_enemy(self, id):
        """ Randomly move an enemy based on its ID (aka its
            position in the enemies list) """

        moves_list = copy.copy(self.cell_list[self.enemies[id]].acc)
        for m in moves_list:
            if m in self.enemies:
                moves_list.remove(m)

        if moves_list != []:
            self.enemies[id] = random.choice(moves_list)
        else:
            pass

    def attack(self, direction):
        """ Based on the requested direction, check if the target cell
            is accessible.  If so, attack into the cell.  Otherwise, break
            down a dividing wall. """

        # Process the given direction to generate a target cell
        # direction 0 = 'up', 1 = 'right', 2 = 'down', 3 = 'left'
        if direction == 0:
            target = self.current_cell - self.width
        elif direction == 1:
            target = self.current_cell + 1
        elif direction == 2:
            target = self.current_cell + self.width
        elif direction == 3:
            target = self.current_cell - 1

        # Test if the target cell is accessible.  If so, check if an enemy
        # is present in that cell.  Remove that enemy if so.  If the target
        # cell is not accessible, remove the wall between the current and
        # target cell instead.
        if self.cell_list[self.current_cell].can_access(target) == 0:
            if target in self.enemies:
                self.enemies.remove(target)
                return 1
            elif target in self.rewards:
                self.rewards.remove(target)
                return 2
            return -1
        else:
            self.remove_wall_pair(self.current_cell, target)
            return 0
