class Instructions:
	def __init__(self):
		self.commands = []

	def __len__(self):
		return len(self.commands)

	@staticmethod
	def dumps(obj):
		return "|".join([Instruction.dumps(instr) for instr in obj.commands])

	@staticmethod
	def loads(input):
		obj = Instructions()
		for line in input.split("|"):
			obj.commands.append(Instruction.loads(line))
		return obj

	def run(self, init, action, cleanup):
		kwargs = init()

		length = len(self.commands)
		for i, command in enumerate(self.commands):
			kwargs["progress"] = float(i) / float(length)
			action(command.mode, command.x, command.y, **kwargs)

		cleanup(**kwargs)

	def add(self, mode, x, y):
		self.commands.append(Instruction(mode, x, y))

	UP, DOWN, MOVE = range(3)

class Instruction:
	def __init__(self, mode, x, y):
		self.mode = int(mode)
		self.x = int(x)
		self.y = int(y)

	@staticmethod
	def dumps(obj):
		return "%d,%d,%d" % (obj.mode, obj.x, obj.y)

	@staticmethod
	def loads(string):
		[mode, x, y] = string.split(",")
		return Instruction(mode, x, y)