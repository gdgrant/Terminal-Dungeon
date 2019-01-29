import os
import curses
from dungeon import Dungeon

# Game parameters
EXPLORATION = 0.5


def make_new_dungeon(height, width):
	""" Generate a new Dungeon object, populate it, and return game state """

	enemies = int(height*width*0.1)
	rewards = max(int(height*width*0.01), 2)
	attacks = max(5,int(enemies * 0.25))

	# Make and populate dungeon
	d = Dungeon(width, height, EXPLORATION)
	d.make_maze()
	d.make_enemies(enemies)
	d.make_rewards(rewards)

	# Make game state
	moves = 0
	score = 0
	done_status = False

	return d, moves, attacks, enemies, score, done_status


def render_layers(stdscr, layers_data, cx, cy, movement=False):

	for i, l in enumerate(layers_data):
		for c in l:
			xpos = c[0] + cx
			ypos = c[1] + cy
			char = c[2]
			stdscr.addstr(ypos, xpos, char, curses.color_pair(i+2))


def key_response(stdscr, d, dirmap, atkmap, enemies, attacks, done_status):

	# Wait for input
	c = stdscr.getkey()
	dscore = 0

	# Designate defaults
	quit_status = False
	reset_status = False

	# If the input matches a control character, respond appropriately
	if c in dirmap.keys() and not done_status:

		# Attempt to move the character
		d.move(dirmap[c])
		dscore = 1

	elif c in atkmap.keys() and not done_status:

		# Attempt to attack an enemy or break wall, if the character
		# has attacks left to make
		if attacks > 0:
			result = d.attack(atkmap[c])

			# If the attack resulted in a killed enemy,
			# record the change in game state
			if result == 1:
				enemies -= 1
				dscore = 10
			elif result == 2:
				dscore = 50

			# Remove one available attack
			attacks -= 1

		else:
			dscore = -1

	elif c == 'q' or c == 'Q':

		# Quit if 'q' is pressed
		quit_status = True

	elif c == 'r' or c == 'R':

		# Reset if 'r' is pressed
		reset_status = True

	return enemies, attacks, dscore, quit_status, reset_status


def main(stdscr):

	# Set up curses
	curses.curs_set(False)
	curses.use_default_colors()

	bkgd  = 17	# Navy blue
	walls = 54	# Black/Gray
	rewar = 3	# Olive
	enemy = 12	# Light blue
	agent = 10	# Green
	curses.init_pair(1, walls, bkgd) # Walls
	curses.init_pair(2, rewar, bkgd) # Rewards
	curses.init_pair(3, enemy, bkgd) # Enemies
	curses.init_pair(4, agent, bkgd) # Player/Target

	# Set up controls
	dirmap = {'w':0, 'a':3, 's':2, 'd':1}
	atkmap = {'W':0, 'A':3, 'S':2, 'D':1}

	# Set up size information
	height, width = stdscr.getmaxyx()

	if height < 14 or width < 60:
		stdscr.addstr(1,1,'Window must be at least 60 x 14 to play!')
		stdscr.addstr(2,1,'Press any key to quit.')
		stdscr.refresh()
		stdscr.getkey()
		quit()

	dheight = (height-10)//2
	dwidth  = (width-3)//2

	dby = dheight * 2 + 1

	# Cue to reset the game
	reset_status = True

	# Begin event loop
	while True:

		# Set up game state
		if reset_status:
			reset_status = False
			d, moves, attacks, enemies, score, done_status = make_new_dungeon(dheight, dwidth)

			stdscr.addstr(dby+7,0,' '*59)
			stdscr.addstr(dby+8,0,' '*59)

		# Move each of the enemies (assuming the player has already
		# moved at least once, to prevent insta-deaths)
		if moves > 0 and not done_status:
			for i in range(enemies):
				d.move_enemy(i)

		# Check for death
		if d.current_cell in d.enemies:
			stdscr.addstr(dby+7,0,'You died!')
			score -= 100 if not done_status else 0
			done_status = True

		# Check for completion
		if d.current_cell == d.cell_ids[-1]:
			finish_score = dheight*dwidth - moves
			if finish_score > 0:
				finish_score_message = 'Well done!'
			else:
				finish_score_message = 'Try moving faster next time...'

			stdscr.addstr(dby+7,0,'Congratulations!  Dungeon complete in {} moves.'.format(moves))
			stdscr.addstr(dby+8,0,'Bonus score: {} {}'.format(finish_score, finish_score_message))
			score += finish_score if not done_status else 0
			done_status = True
		
		# Obtain dungeon render
		layer0, layers = d.render()
		corner_x = 1
		corner_y = 1

		# Render the maze
		for i, l in enumerate(layer0):
			stdscr.addstr(corner_y+i,corner_x, l, curses.color_pair(1))

		render_layers(stdscr, layers, corner_x, corner_y)

		stdscr.addstr(dby+2,0,'[wasd] to move.               | Moves:        {:<4}'.format(moves))
		stdscr.addstr(dby+3,0,'Shift+[wasd] to attack.       | Attacks left: {:<4}'.format(attacks))
		stdscr.addstr(dby+4,0,'[r] to reset, [q] to quit.    | Enemies left: {:<4}'.format(enemies))
		stdscr.addstr(dby+5,0,'Goal: Reach the bottom right. | Score:        {:<4}'.format(score))

		# Refresh the screen
		stdscr.refresh()

		# Respond to key input
		enemies, attacks, dscore, quit_status, reset_status = \
			key_response(stdscr, d, dirmap, atkmap, enemies, attacks, done_status)
		score += dscore

		# Quit if requested
		if quit_status:
			break

		# Iterate the move counter and go back to the start of the loop
		moves += 1 if not done_status else 0

if __name__ == '__main__':
	curses.wrapper(main)
	curses.endwin()