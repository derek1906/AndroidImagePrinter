import math
from pprint import pprint

class Point(object):
	def __init__(self, x, y):
		self.x = int(x)
		self.y = int(y)

	def __repr__(self):
		return "({}, {})".format(self.x, self.y)

class Line(object):
	def __init__(self, p1, p2):
		self.p1 = p1
		self.p2 = p2

		if p1.x - p2.x == 0:
			self.slope = math.copysign(float("Inf"), p1.y - p2.y)
		else:
			self.slope = float(p1.y - p2.y) / float(p1.x - p2.x)

	def isHorizontal(self):
		return self.slope == 0
	
	def getYMin(self):
		return min(self.p1.y, self.p2.y)
	
	def getYMax(self):
		return max(self.p1.y, self.p2.y)
	
	def getDxOverDy(self):
		return 1. / self.slope;
	
	def getX(self, y):
		if self.slope == 0.:
			# cannot get x
			raise Exception("Slope is 0.")
		if self.p1.x == self.p2.x:
			# straight line
			return self.p1.x

		return float(self.slope * self.p1.x + y - self.p1.y) / (self.slope)

	def __repr__(self):
		return "{}->{}".format(self.p1, self.p2)


class Polygon(object):
	def __init__(self, lines):
		if len(lines) < 2:
			raise Error("Not a valid polygon (Length < 2).")

		self.edges = lines

	'''
	 * Algorithm from UIUC CS418 "Rasterization.pptx" by John C. Hart.
	 * Modified to create space filling lines and arbitrary y stepsizes.
	 *
	 * Space filling is based on an odd parity policy, i.e. in a scan line,
	 * only the space between every pair of lines is filled.
	 *
	 * For example, in S = [x1, x2, x3, x4], only the space between
	 * (x1 & x2), (x3 & x4) will be filled.
	'''
	def calculateFillingLines(self, hSpace=5, minLength=5):

		# 1: Ignore horizontal edges
		edges = [
			{"edge": edge, "yMin": edge.getYMin()}
			for edge in self.edges
			if not edge.isHorizontal()
		]

		#2. Sort edges by smaller y coordinate
		edges.sort(key=lambda x: x["yMin"])

		edgeIndex = 0
		fillingLines = []
		rasterizingEdges = []
		initY = edges[0]["edge"].getYMin()
		y = initY
		i = 0

		#rasterization main loop
		while True:
			# 1: Delete y >= ymax edges
			rasterizingEdges = [edge for edge in rasterizingEdges if edge["yMax"] > y]
			# 2: Update x
			for edge in rasterizingEdges:
				edge["x"] = edge["edge"].getX(y)
			# 3: Add edges where y <= ymin
			nextEdgeY = None
			while edgeIndex < len(edges):
				edge = edges[edgeIndex]
				if edge["yMin"] <= y:
					rasterizingEdges.append({
						"edge"    	: edge["edge"],
						"x"       	: edge["edge"].getX(y),
						"dxOverDy"	: edge["edge"].getDxOverDy(),
						"yMax"    	: edge["edge"].getYMax()
					})
				else:
					nextEdgeY = edge["yMin"]
					break

				edgeIndex += 1

			if nextEdgeY == None:
				nextEdgeY = float("inf")

			# Modified: Output lines according to step size
			if (y - initY) % hSpace == 0:
				# 4: Sort by x and dx/dy
				rasterizingEdges.sort(key=lambda edge: (edge["x"], edge["dxOverDy"]))
				# 5: For each pair of x, draw a line
				if len(rasterizingEdges) % 2:
					# Check if polygon is invalid
					raise Exception("Invalid polygon (crossed an odd number of lines in a scan line.)")

				for index in xrange(0, len(rasterizingEdges), 2):
					p1 = Point(rasterizingEdges[index]["x"]    	, y)
					p2 = Point(rasterizingEdges[index + 1]["x"]	, y)

					if p2.x - p1.x < minLength:
						# Skip lines that are shorter than minLength
						continue

					fillingLines.append(Line(p1, p2))

			# 6: Increase y
			nextStepsizeY = (i + 1) * hSpace + initY
			if nextEdgeY < nextStepsizeY:
				# Skip to next edge ymin
				y = nextEdgeY
			else:
				# Skip to next step size
				y = nextStepsizeY
				i += 1
		
			if len(rasterizingEdges) == 0:
				break

		return fillingLines

	def join(self, other):
		return Polygon(self.edges + other.edges)

	def __repr__(self):
		return repr(self.edges)


class Triangle(Polygon):
	def __init__(self, p1, p2, p3):
		super(Triangle, self).__init__([
			Line(p1, p2),
			Line(p2, p3),
			Line(p3, p1)
		])


class Circle(Polygon):
	def __init__(self, center, r, fragmentSize):
		fragments = int(math.pi * 2 * r / fragmentSize)

		stepsize = math.pi * 2 / fragments
		points = []
		lines = []

		for i in xrange(fragments):
			angle = stepsize * i
			points.append(Point(
				math.cos(angle) * r + center.x,
				math.sin(angle) * r + center.y
			))

		for i in xrange(fragments):
			lines.append(Line(
				points[i],
				points[(i + 1) % fragments]
			))

		super(Circle, self).__init__(lines)
		self.center = center
		self.r = r