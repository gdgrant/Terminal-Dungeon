### Maze class for 2-D maze module
### Author:   gdgrant
### Date:     11/6/2018

import copy
import random
from cell import Cell

# All the characters used for rendering the maze
char_dict = {
	0   : ' ',
	1   : '─',
	2   : '│',
	3   : '┌',
	4   : '─',
	5   : '─',
	6   : '┐',
	7   : '┬',
	8   : '│',
	9   : '└',
	10  : '│',
	11  : '├',
	12  : '┘',
	13  : '┴',
	14  : '┤',
	15  : '┼',
}

class Maze:
	""" A 2-D maze generator and renderer, including navigation system """

	def __init__(self, width, height, exploration=0.):
		""" Set the maze's width, height, list of cells,
			and exploration parameter """

		self.width      = width
		self.height     = height
		self.cell_ids   = list(range(width*height))
		self.exploration = exploration

		# Make each cell with the proper connections using the Cell class
		self.make_cells()
		self.current_cell = 0


	def __str__(self):
		print_rows, _ = self.render(layer_override=0)
		return '\n'.join(print_rows)


	def render(self, layer_override=1):
		""" Return the maze as a rendered drawing,
			including player position """

		# Set up of rows of characters
		print_rows = ['' for _ in range(self.height*2+1)]
		layers = []

		# Iterate over all cells in maze
		for i in self.cell_ids:

			# Identify row and column of this cell
			row = i//self.width
			col = i%self.width

			# Determine whether cells immediately above or to the left
			# are accessible (value of 0 if accessible, -1 if not)
			a = self.cell_list[i].can_access(i-self.width)
			b = self.cell_list[i].can_access(i-1)

			# Select the wall characters around this cell based on
			# accessibility of other cells (a and b)
			wall_a = ' ' if a == 0 else '─'
			wall_b = ' ' if b == 0 else '│'

			# Depending on the current row and column, select the appropriate
			# junction character for clean rendering
			if row != 0 and col != 0:
				# If not in the 0th row or column, use all four cells about
				# the junction to the upper left of the current cell to
				# determine the appropriate junction character
				c = self.cell_list[i-(self.width+1)].can_access(i-1)
				d = self.cell_list[i-(self.width+1)].can_access(i-self.width)

				# Pattern ranges from 0 to 15
				pattern = -1*a + -2*b + -4*c + -8*d
				jun = char_dict[pattern]

			elif row != 0 and col == 0:
				# Get junction pattern for the 0th column
				pattern = -1*a + 2 + 8
				jun = char_dict[pattern]

			elif row == 0 and col != 0:
				# Get junction pattern for the 0th row
				pattern = 1 + 4 + -2*b
				jun = char_dict[pattern]

			elif row == 0 and col == 0:
				# Get junction pattern for the 0th row, 0th column
				jun = '┌'

			# Get the appropriate character for the contents of the cell
			state, layer = self.cell_state_render(i)

			# Override layer if desired
			layer *= layer_override

			# Record state and current position if layer is not 0
			if layer != 0:
				while len(layers) < layer: layers.append([])
				xpos = 2*col + 1
				ypos = 2*row + 1
				cdata = (xpos, ypos, state)
				layers[layer-1].append(cdata)

			# Collect the junction, walls, and cell contents and append them
			# to the rows of characters.  Only layer 0 is used here.
			cstate = state if layer == 0 else ' '
			print_rows[2*row]   += (jun + wall_a)
			print_rows[2*row+1] += (wall_b + cstate)

		# Complete the bottom row of characters
		for i in range(self.width):

			# Make ID and column
			id = i + self.width*(self.height-1)
			col = id%self.width

			# If in the 0th column, make 'bottom left' character
			# Otherwise, check the accessibility of the cell to the left
			# and choose the junction character accordingly
			if i == 0:
				jun = '└'
			else:
				b = self.cell_list[id].can_access(id-1)
				pattern = 1 + 4 + -8*b
				jun = char_dict[pattern]

			# Append the boundary and boundary junction for each cell
			print_rows[-1] += jun + '─'

		# Complete the rightmost column of characters
		for i in range(self.height):

			# Make ID, row, and column
			id = self.width*(i+1) - 1
			col = id%self.width
			row = id//self.width

			# If in the last column, make 'upper right' character
			# Otherwise, check the accessibility of the cell direcly above
			# and choose the junction character accordingly
			if i == 0:
				jun = '┐'
			else:
				a = self.cell_list[id].can_access(id-self.width)
				pattern = 2 + -4*a + 8
				jun = char_dict[pattern]

			# Append the boundary and boundary junction for each cell
			print_rows[2*row] += jun
			print_rows[2*row+1] += '│'

		# Put the 'lower right' character at the end of the last character row
		print_rows[-1] += '┘'

		# Join the list of rows into a block of rendered text and return
		return print_rows, layers


	def cell_state_render(self, i):
		""" Render the symbol for the current player or an empty space """
		state = 'x' if i == self.current_cell else ' '
		layer = 1 if i == self.current_cell else 0
		return state, layer


	def make_cells(self):
		""" Generate the list of cells used in the maze """

		# Make the list
		self.cell_list = []

		# Iterate over all cell ids
		for i in self.cell_ids:

			# Get the row and column of this cell
			row = i//self.width
			col = i%self.width

			# Collect adjacent cells
			adj = []

			# Based on the column, include the requisite adjacent cells
			if col == 0:
				adj.append(i+1)
			elif col == self.width-1:
				adj.append(i-1)
			else:
				adj.extend([i-1, i+1])

			# Based on the row, include the requisite adjacent cells
			if row == 0:
				adj.append(i+self.width)
			elif row == self.height-1:
				adj.append(i-self.width)
			else:
				adj.extend([i-self.width, i+self.width])

			# When initializing the cells, make the accessible cells equal
			# to the adjacent cells
			acc = copy.copy(adj)

			# Append a Cell object to the cell list
			self.cell_list.append(Cell(i, adj, acc))

		return 0


	def initialize_walls(self):
		""" Make all connections between cells walls """

		for id_a in self.cell_ids:
			for id_b in self.cell_ids[id_a:]:
				self.make_wall_pair(id_a, id_b)


	def make_wall_pair(self, id_a, id_b):
		""" Between two cells, make a wall """

		a = self.cell_list[id_a].block_access(id_b)
		b = self.cell_list[id_b].block_access(id_a)
		return a + b


	def remove_wall_pair(self, id_a, id_b):
		""" Between two cells, remove a wall """

		a = self.cell_list[id_a].make_access(id_b)
		b = self.cell_list[id_b].make_access(id_a)
		return a + b


	def make_maze(self):
		""" Using a depth-first search with a curiosity parameter, generate
			a new maze design """

		# Set all connections to walls
		self.initialize_walls()

		# Generate a starting list of unvisited cells
		unvisited_cells = copy.copy(self.cell_ids)
		unvisited_cells.remove(self.current_cell)

		# Set up a stack and start the depth search loop
		stack = [self.current_cell]
		while unvisited_cells != []:

			# Determine which adjacent cells are visited or unvisted
			unv_adj = [c for c in self.cell_list[self.current_cell].adj if c in unvisited_cells]
			vis_adj = [c for c in self.cell_list[self.current_cell].adj if not c in unvisited_cells and (len(stack)>0 and c != stack[-1])]

			# If there are unvisited adjacent cells, proceed.  Otherwise,
			# retrace back through the stack
			if unv_adj:

				# If the curiosity parameter is satisfied, use depth-first
				# search.  Otherwise, if there are adjacent previously visited
				# cells, make a tertiary selection.  If neither of those things
				# occurs, pass to the next iteration
				if random.random() > self.exploration:

					# Randomly select the next cell from the list of unvisited
					# cells and remove the walls blocking the movement
					next = random.choice(unv_adj)
					self.remove_wall_pair(self.current_cell, next)

					# Record the next cell in the stack, remove the cell ID
					# from the list of unvisited cells, and complete the
					# movement by setting the new current cell
					stack.append(next)
					if next in unvisited_cells:
						unvisited_cells.remove(next)
					self.current_cell = next

				elif not vis_adj == []:

					# Randomly select the next cell from the list of visited
					# cells and remove the walls blocking the movement
					next = random.choice(vis_adj)
					self.remove_wall_pair(self.current_cell, next)

					# Record the next cell in the stack, remove the cell ID
					# from the list of unvisited cells, and complete the
					# movement by setting the new current cell
					stack.append(next)
					if next in unvisited_cells:
						unvisited_cells.remove(next)
					self.current_cell = next

				else:

					# Do nothing if neither of the other conditions is satisfied
					pass

			else:

				# If the stack is not empty, pop the last element
				# If the stack is empty, choose a random unvisited cell from
				#    which to start anew.  This effectively restarts the stack
				#    if the curiosity parameter has gotten the depth-first
				#    search algorithm stuck in some corner of visited cells.
				if stack != []:
					self.current_cell = stack.pop(-1)
				else:
					ves = random.choice(unvisited_cells)
					self.current_cell = random.choice([c for c in self.cell_list[ves].adj])

		# Set the starting cell to the upper left, and return
		self.current_cell = 0
		return 0


	def move(self, direction):
		""" Based on the requested direction, check if the target cell
			is accessible and move there if so """

		# Process the given direction to generate a target cell
		# Direction key:  0 = 'up', 1 = 'right', 2 = 'down', 3 = 'left'
		if direction == 0:
			target = self.current_cell - self.width
		elif direction == 1:
			target = self.current_cell + 1
		elif direction == 2:
			target = self.current_cell + self.width
		elif direction == 3:
			target = self.current_cell - 1

		# Test if the target cell is accessible, and set the current cell
		# to the target if so.
		if self.cell_list[self.current_cell].can_access(target) == 0:
			self.current_cell = target
			return 0
		else:
			return -1
