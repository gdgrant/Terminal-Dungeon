### A small 2-D dungeon-crawling game
### Author:   gdgrant
### Date:     11/6/2018

import os
import msvcrt
from dungeon import Dungeon

# Game parameters
HEIGHT        = 20
WIDTH         = 39
NUM_ENEMIES   = 80
ATTACKS       = 20
EXPLORATION   = 0.2


def clear_screen():
    """ Clear the screen in a system-aware manner """
    os.system('cls' if os.name == 'nt' else 'clear')


def make_new_dungeon():
    """ Generate a new Dungeon object, populate it, and return game state """

    # Make and populate dungeon
    d = Dungeon(WIDTH, HEIGHT, EXPLORATION)
    d.make_maze()
    d.make_enemies(NUM_ENEMIES)

    # Make game state
    moves = 0
    attacks = ATTACKS
    enemies = NUM_ENEMIES

    return d, moves, attacks, enemies


def main():

    # Set up game state
    d, moves, attacks, enemies = make_new_dungeon()

    # Set up controls
    dirmap = {b'w':0, b'a':3, b's':2, b'd':1}
    atkmap = {b'W':0, b'A':3, b'S':2, b'D':1}

    # Begin event loop
    while True:

        # Move each of the enemies (assuming the player has already
        # moved at least once, to prevent insta-deaths)
        if moves > 0:
            for i in range(enemies):
                d.move_enemy(i)

        # Print the dungeon after clearing the screen
        clear_screen()
        print(d)

        # Print display messages and current game state
        print('[wasd] to move, [q] to quit.  | Moves: {}'.format(moves))
        print('Shift+[wasd] to attack.       | Attacks left: {}'.format(attacks))
        print('Goal: Reach the bottom right. | Enemies left: {}'.format(enemies))

        # Check for death
        if d.current_cell in d.enemies:
            print('You died!')
            quit()

        # Check for completion
        if d.current_cell == d.cell_ids[-1]:
            print('Congratulations!  Dungeon complete in {} moves.\n'.format(moves))
            quit()

        # Wait for input
        c = msvcrt.getch()

        # If the input matches a control character, respond appropriately
        if c in dirmap.keys():

            # Attempt to move the character
            d.move(dirmap[c])

        elif c in atkmap.keys():

            # Attempt to attack an enemy or break wall, if the character
            # has attacks left to make
            if attacks > 0:
                result = d.attack(atkmap[c])

                # If the attack resulted in a killed enemy,
                # record the change in game state
                if result == 1:
                    enemies -= 1

                # Remove one available attack
                attacks -= 1

        elif c == b'q':

            # Quit if 'q' is pressed
            quit()

        # Iterate the move counter and go back to the start of the loop
        moves += 1


if __name__ == '__main__':
    main()
