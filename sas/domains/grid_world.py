from ..operators import *

class MoveGrid(Action):
	def __init__(self, position, direction):
		super(self.__class__, self).__init__(arg_info(currentframe()))
		self.conditions = {'robot': position}
		self.effects = {'robot': (position[0] + direction[0], position[1] + direction[1])}

def move_grid(n=10, m=10):
	initial = State({'robot': (0, 0)})
	goal = Goal({'robot': (n-1, m-1)})

	directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
	#directions = list(product([-1, 0, 1], repeat=2))

	operators = []
	x_range, y_range = range(n), range(m)
	for x in x_range:
		for y in y_range:
			for direction in directions:
				if (x + direction[0]) in x_range and (y + direction[1]) in y_range:
					operators.append(MoveGrid((x, y), direction))

	return initial, goal, operators
