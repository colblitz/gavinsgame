import random
import itertools
import time

MOVE_MIN = 2
MOVE_MAX = 27
MOVE_MAXR = MOVE_MAX + 1

def divides_into(a, b):
	return a < b and (b % a == 0)

move_points = {}
for m0 in range(MOVE_MIN, MOVE_MAXR):
	move_points[m0] = {}
	for m1 in range(MOVE_MIN, MOVE_MAXR):
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

# for m0 in move_points:
# 	print move_points[m0]

def index_min(values):
  return min(xrange(len(values)),key=values.__getitem__)

def index_max(values):
  return max(xrange(len(values)),key=values.__getitem__)

class Mover(object):
	def __init__(self, name):
		self.name = name

	def get_move(self, sets, history, player):
		raise NotImplementedError("get_move not implemented for " + type(self).__name__)

	def get_type(self):
		return type(self).__name__

class RandomMover(Mover):
	def get_move(self, sets, history, player):
		return random.choice(sets[player])

class PickHighestMover(Mover):
	def get_move(self, sets, history, player):
		return sets[player][-1]

class PickLowestMover(Mover):
	def get_move(self, sets, history, player):
		return sets[player][0]

class PickBestProbability(Mover):
	def get_move(self, sets, history, player):
		scores = [0 for m in sets[player]]
		for mi, m in enumerate(sets[player]):
			for o in sets[1 - player]:
				scores[mi] += move_points[o if player else m][m if player else o][player]
				# if m == 27:
				# 	print "i play 27 vs " + str(o) + " to get " + str(move_points[m][o][player])
		# print sets[player]
		# print scores
		bests = 0
		bestsi = []
		for si, s in enumerate(scores):
			if s > bests:
				bestsi = [si]
				bests = s
			elif s == bests:
				bestsi.append(si)

		return sets[player][random.choice(bestsi)]

class PickWorstProbability(Mover):
	def get_move(self, sets, history, player):
		scores = [0 for m in sets[player]]
		for mi, m in enumerate(sets[player]):
			for o in sets[1 - player]:
				scores[mi] += move_points[o if player else m][m if player else o][player]
				# if m == 27:
				# 	print "i play 27 vs " + str(o) + " to get " + str(move_points[m][o][player])
		# print sets[player]
		# print scores
		bests = 26
		bestsi = []
		for si, s in enumerate(scores):
			if s < bests:
				bestsi = [si]
				bests = s
			elif s == bests:
				bestsi.append(si)

		return sets[player][random.choice(bestsi)]

class Game(object):
	def __init__(self, player0, player1):
		self.movers = [player0, player1]
		self.sets = [range(MOVE_MIN, MOVE_MAXR), range(MOVE_MIN, MOVE_MAXR)]
		self.round = 0
		self.points = [0, 0]
		self.done = False
		self.history = []

	def make_move(self):
		if not self.done:

			if len(self.sets[0]) > 1:
				move0 = self.movers[0].get_move(self.sets, self.history, 0)
				self.sets[0].remove(move0)

				move1 = self.movers[1].get_move(self.sets, self.history, 1)
				self.sets[1].remove(move1)
			else:
				move0 = self.sets[0].pop()
				move1 = self.sets[1].pop()

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
		# self.print_state()

	def reward(self, player):
		if self.is_done():
			if self.points[player] == 13:
				return 0.5
			return 1 if self.points[player] > self.points[1 - player] else 0
		return 0

	def winner(self):
		if self.is_done():
			if self.points[0] == self.points[1]:
				return 0.5
			return 0 if self.points[0] > self.points[1] else 1

class Tournament(object):
	def __init__(self, players):
		self.players = players
		self.reset()

	def reset(self):
		self.round = 0
		self.scores = [0 for p in self.players]
		self.table = [[0 for p in self.players] for p in self.players]
		self.elapsed = 0

	def play(self, rounds):
		start = time.clock()
		for i in xrange(rounds):
			for pair in itertools.combinations(range(len(self.players)), 2):
				p0 = self.players[pair[0]]
				p1 = self.players[pair[1]]
				g = Game(p0, p1)
				g.play_game()
				self.scores[pair[0]] += g.reward(0)
				self.scores[pair[1]] += g.reward(1)
				self.table[pair[0]][pair[1]] += g.reward(0)
				self.table[pair[1]][pair[0]] += g.reward(1)
		self.round += rounds
		end = time.clock()
		self.elapsed += end - start

	def print_status(self):
		print "----------------------------------"
		print "%d Rounds in %f time (%f s/round)" % (self.round, self.elapsed, self.elapsed / self.round)
		for pi, p in enumerate(self.players):
			print "%d: %s" % (pi, p.get_type())
		print "".join([str(x).rjust(8) for x in [""] + range(len(self.players))])

		# print "".join(["%12s" % x for x in ])
		# print "".join(['{:>12}'.format(x) for x in ([""] + [p.name() for p in self.players])])
		for ri in range(len(self.table)):
			r = self.table[ri]
			t = self.scores[ri]
			p = self.players[ri]
			print "".join([str(x).rjust(8) for x in [ri] + r + [t]])
		 	# print '{:>12}'.format(p.name())

		# print "".join(['{:>10}'.format(x) for x in self.scores])
		# for r in self.table:
		# 	print "".join(['{:>10}'.format(x) for x in r])

# def pad(x, n):
# 	return ('{:>' + str(n) + '}').format(x)

# print pad(135135, 10)

t = Tournament([RandomMover("Player 0"),
               PickHighestMover("Player 1"),
               PickLowestMover("Player 2"),
               PickBestProbability("Player 3"),
               PickWorstProbability("Player 4")])
t.play(5000)
t.print_status()

# g = Game(RandomMover("player0"), PickBestProbability("player1"))
# g.play_game()
# g.print_state()

# g = Game(RandomMover("player0"), PickBestProbability("player1"))
# g.play_game()
# g.print_state()

# g = Game(RandomMover("player0"), PickBestProbability("player1"))
# g.play_game()
# g.print_state()

# g = Game(RandomMover("player0"), PickBestProbability("player1"))
# g.play_game()
# g.print_state()

# g = Game(RandomMover("player0"), RandomMover("player1"))
# g.play_game()

# g = Game(RandomMover("player0"), PickHighestMover("player1"))
# g.play_game()

# g = Game(RandomMover("player0"), PickLowestMover("player1"))
# g.play_game()
