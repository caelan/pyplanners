from ..operators import *

class MoveArm(Action):
	def __init__(self, position, direction):
		super(self.__class__, self).__init__(arg_info(currentframe()))
		self.conditions = {
			'robot': position,
			'hand': False
		}
		self.effects = {
			'robot': position + direction,
		}

class MoveArmHolding(Action):
	def __init__(self, position, direction, block):
		super(self.__class__, self).__init__(arg_info(currentframe()))
		self.conditions = {
			'robot': position,
			'hand': block,
			block: position,
			('clear', position + direction): True
		}
		self.effects = {
			'robot': position + direction,
			block: position + direction,
			('clear', position): True,
			('clear', position + direction): False
		}

class Pick(Action):
	def __init__(self, position, block):
		super(self.__class__, self).__init__(arg_info(currentframe()))
		self.conditions = {
			'robot': position,
			'hand': False,
			block: position
		}
		self.effects = {
			'hand': block
		}

class Place(Action):
	def __init__(self, position, block):
		super(self.__class__, self).__init__(arg_info(currentframe()))
		self.conditions = {
			'robot': position,
			'hand': block,
			block: position
		}
		self.effects = {
			'hand': False
		}

def shift_blocks(n=2):
	blocks = ['block%s'%i for i in range(1, n+1)]
	positions = range(n+1)
	directions = [-1, 1]
	#directions = [-1, 0, 1]

	initial = State(merge_dicts(
			{'robot': 0, ('clear', n): True},
			{block: i for i, block in enumerate(blocks)}))

	goal = Goal({
		'hand': False,
		'block1': 1
	})

	operators = []
	for position in positions:
		for direction in directions:
			if position + direction in positions:
				operators.append(MoveArm(position, direction))
				for block in blocks:
					operators.append(MoveArmHolding(position, direction, block))

	for position in positions:
		for block in blocks:
			operators.append(Pick(position, block))
			operators.append(Place(position, block))

	return initial, goal, operators
