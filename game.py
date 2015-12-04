import random

def divides_into(a, b):
	return a < b and (b % a == 0)

move_points = {}
for m0 in range(2, 27):
	move_points[m0] = {}
	for m1 in range(2, 27):
		if m0 == m1:
			move_points[m0][m1] = [0.5, 0.5]
		elif divides_into(m0, m1):
			move_points[m0][m1] = [0, 1]
		elif divides_into(m1, m0):
			move_points[m0][m1] = [1, 0]
		elif m0 < m1:
			move_points[m0][m1] = [1, 0]
		elif m1 < m0:
			move_points[m0][m1] = [0, 1]
		else:
			print "what"

class Mover(object):
	def __init__(self, name):
		self.name = name

	def get_move(self, sets, player):
		raise NotImplementedError("get_move not implemented for " + type(self).__name__)

	def get_type(self):
		return type(self).__name__

class RandomMover(Mover):
	def __init__(self, name):
		self.name = name

	def get_move(self, sets, player):
		return random.choice(sets[player])

class PickHighestMover(Mover):
	def __init__(self, name):
		self.name = name

	def get_move(self, sets, player):
		return sets[player][-1]

class PickLowestMover(Mover):
	def __init__(self, name):
		self.name = name

	def get_move(self, sets, player):
		return sets[player][0]

class Game(object):
	def __init__(self, player0, player1):
		self.movers = [player0, player1]
		self.sets = [range(2, 27), range(2, 27)]
		self.round = 0
		self.points = [0, 0]
		self.done = False
		self.history = []

	def make_move(self):
		if not self.done:
			move0 = self.movers[0].get_move(self.sets, 0)
			self.sets[0].remove(move0)

			move1 = self.movers[1].get_move(self.sets, 1)
			self.sets[1].remove(move1)

			points = move_points[move0][move1]
			self.points[0] += points[0]
			self.points[1] += points[1]

			self.history.append([move0, move1, self.points[0], self.points[1]])

			# print "     Making move: " + str(move0) + " - " + str(move1)
			# print "                  " + str(points)

			self.round += 1
			if len(self.sets[0]) == 0:
				self.done = True

	def print_state(self):
		print "--- Round " + str(self.round) + " -----------------------------"
		print "0 - " + self.movers[0].get_type() + " " + self.movers[0].name + ": " + str(self.points[0]) + " | " + str(self.sets[0])
		print "1 - " + self.movers[1].get_type() + " " + self.movers[1].name + ": " + str(self.points[1]) + " | " + str(self.sets[1])
		if self.done:
			self.pretty_print_history()

	def pretty_print_history(self):
		t = zip(*self.history)
		for l in t:
			print "".join(['{:>5}'.format(x) for x in l])

	def is_done(self):
		return self.done

	def play_game(self):
		while not self.is_done():
			self.make_move()
		self.print_state()

g = Game(RandomMover("player0"), RandomMover("player1"))
g.play_game()

g = Game(RandomMover("player0"), PickHighestMover("player1"))
g.play_game()

g = Game(RandomMover("player0"), PickLowestMover("player1"))
g.play_game()
