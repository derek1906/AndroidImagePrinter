# This files read an "input.svg".
# 
# python path_to_points.py | ~/Library/Android/sdk/tools/monkeyrunner ~/test_move.py

from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier, parse_path
import sys, json, sys, xml.etree.ElementTree
import numpy as np
import math
from instructions import Instructions
import shapes

'''
	Returns a lambda that takes in t: [0, 1]
'''
def bezier_sample(start, control1, control2, end):
	inputs = np.array([start, control1, control2, end])
	cubic_bezier_matrix = np.array([
		[-1, 3, -3, 1],
		[3, -6, 3, 0],
		[-3, 3, 0, 0],
		[1, 0, 0, 0]
	])

	partial = cubic_bezier_matrix.dot(inputs)

	return (lambda t: np.array([t**3, t**2, t, 1]).dot(partial))

'''
	W3 SVG 1.1 Appendix F.6.5 "Conversion from endpoint to center parameterization"
	https://www.w3.org/TR/SVG/implnote.html#ArcConversionEndpointToCenter
'''
def arc_sample(start, radius, rotation, fArc, fSweep, end):
	x1 = start[0]
	y1 = start[1]
	x2 = end[0]
	y2 = end[1]
	rx = radius[0]
	ry = radius[1]

	def angle(u, v):
		(ux, uy) = u.flatten().tolist()
		(vx, vy) = v.flatten().tolist()

		theta = math.acos(u.T.dot(v) / math.sqrt(u.T.dot(u)) / math.sqrt(v.T.dot(v)))
		return math.copysign(theta, ux * vy - uy * vx)

	# Step 1: Compute (x1', y1') start prime
	sp = np.array([
		[math.cos(rotation), math.sin(rotation)],
		[-math.sin(rotation), math.cos(rotation)]
	]).dot(np.array([
		[(x1 - x2) / 2.],
		[(y1 - y2) / 2.]
	]))
	(x1p, y1p) = sp.flatten().tolist()
	# Step 2: Compute (cx', cy') center prime
	cp = math.sqrt(
		(rx**2 * ry**2 - rx**2 * y1p**2 - ry**2 * x1p**2) / 
		(rx**2 * y1p**2 + ry**2 * x1p**2)
	) * np.array([
		[rx * y1p / ry],
		[-ry * x1p / rx]
	])
	if fArc == fSweep:
		cp = -cp
	(cxp, cyp) = cp.flatten().tolist()
	# Step 3: Compute (cx, cy)
	c = np.array([
		[math.cos(rotation), -math.sin(rotation)],
		[math.sin(rotation), math.cos(rotation)]
	]).dot(cp) + np.array([
		[(x1 + x2) / 2.],
		[(y1 + y2) / 2.]
	])
	(cx, cy) = c.flatten().tolist()
	# Step 4: Compute theta1 and delta theta
	theta1 = angle(
		np.array([[1], [0]]),
		np.array([
			[(x1p - cxp) / rx],
			[(y1p - cyp) / ry]
		])
	)
	dTheta = angle(
		np.array([
			[(x1p - cxp) / rx],
			[(y1p - cyp) / ry]
		]),
		np.array([
			[(-x1p - cxp) / rx],
			[(-y1p - cyp) / ry]
		])
	) % (2 * math.pi)
	if fSweep == False and dTheta > 0:
		dTheta -= 2 * math.pi
	elif fSweep == True and dTheta < 0:
		dTheta += 2 * math.pi

	# Construct final values
	center = (cx, cy)
	theta1 = theta1
	dTheta = dTheta

	'''
	   	W3 SVG 1.1 Appendix F.6.3 "Parameterization alternatives"
	'''	
	def compute_from_center(t):
		theta = t * dTheta + theta1
		point = np.array([
			[math.cos(rotation), -math.sin(rotation)],
			[math.sin(rotation), math.cos(rotation)]
		]).dot(np.array([
			[rx * math.cos(theta)],
			[ry * math.sin(theta)]
		])) + c
		return point.flatten().tolist()

	return compute_from_center


def insertMove(commands, start, end):
	MAX_DIST = 10

	dist = math.sqrt((start[0] - end[0])**2 + (start[1] - end[1])**2)
	if dist > MAX_DIST:
		segments = int(dist / MAX_DIST)
		for i in xrange(segments):
			t = float(i + 1) / float(segments)
			x = (end[0] - start[0]) * t + start[0]
			y = (end[1] - start[1]) * t + start[1]
			commands.add(Instructions.MOVE, x, y)
	else:
		commands.add(Instructions.MOVE, end[0], end[1])


def generateCommandsFromSVGPath(commands, path, fill=False, sample_size=10):
	path = parse_path(path)

	edges = []
	prev_end = None
	for line in path:
		start	= (int(line.start.real)	, int(line.start.imag))
		end  	= (int(line.end.real)  	, int(line.end.imag))

		#print("{} -> {}".format(start, end))

		if start == end:
			# ignore zero length lines
			continue

		if prev_end == None:
			# first point
			commands.add(Instructions.DOWN, start[0], start[1])
		elif prev_end != start:
			# new line
			commands.add(Instructions.UP, prev_end[0], prev_end[1])
			commands.add(Instructions.DOWN, start[0], start[1])


		# Line
		if isinstance(line, Line):
			# move to end
			insertMove(commands, start, end)
			# build a line
			edges.append(shapes.Line(
				shapes.Point(start[0], start[1]),
				shapes.Point(end[0], end[1])
			))
		# CubicBezier
		elif isinstance(line, CubicBezier):
			# sample points
			curve_start = (line.start.real, line.start.imag)
			curve_ctrl1 = (line.control1.real, line.control1.imag)
			curve_ctrl2 = (line.control2.real, line.control2.imag)
			curve_end = (line.end.real, line.end.imag)
			curve = bezier_sample(curve_start, curve_ctrl1, curve_ctrl2, curve_end)

			prev_curve_point = curve_start
			for i in xrange(sample_size):
				t = float(i + 1) / float(sample_size)
				point = curve(t)
				commands.add(Instructions.MOVE, point[0], point[1])
				edges.append(shapes.Line(
					shapes.Point(prev_curve_point[0], prev_curve_point[1]),
					shapes.Point(point[0], point[1])
				))
				prev_curve_point = point
		# QuadraticBezier
		elif isinstance(line, QuadraticBezier):
			curve_start = (line.start.real, line.start.imag)
			curve_ctrl = (line.control.real, line.control.imag)
			curve_end = (line.end.real, line.end.imag)
			curve = bezier_sample(curve_start, curve_ctrl, curve_ctrl, curve_end)

			prev_curve_point = curve_start
			for i in xrange(sample_size):
				t = float(i + 1) / float(sample_size)
				point = curve(t)
				commands.add(Instructions.MOVE, point[0], point[1])
				edges.append(shapes.Line(
					shapes.Point(prev_curve_point[0], prev_curve_point[1]),
					shapes.Point(point[0], point[1])
				))
				prev_curve_point = point
		# Arc
		else:
			curve = arc_sample(
				(line.start.real, line.start.imag),
				(line.radius.real, line.radius.imag),
				line.rotation / 180 * math.pi,
				line.arc,
				line.sweep,
				(line.end.real, line.end.imag)
			)

			prev_curve_point = (line.start.real, line.start.imag)
			for i in xrange(sample_size):
				t = float(i + 1) / float(sample_size)
				point = curve(t)
				commands.add(Instructions.MOVE, point[0], point[1])
				edges.append(shapes.Line(
					shapes.Point(prev_curve_point[0], prev_curve_point[1]),
					shapes.Point(point[0], point[1])
				))
				prev_curve_point = point

		prev_end = end

	# release touch
	commands.add(Instructions.UP, prev_end[0], prev_end[1])

	polygon = shapes.Polygon(edges)
	if fill:
		fillingLines = polygon.calculateFillingLines(2)
		for line in fillingLines:
			commands.add(Instructions.DOWN, line.p1.x, line.p1.y)
			insertMove(commands, (line.p1.x, line.p1.y), (line.p2.x, line.p2.y))
			commands.add(Instructions.UP, line.p2.x, line.p2.y)

	return commands

def normalizeCommands(commands, scale=1):
	screensize = (1440, 2560)

	minX, maxX = min(commands.commands, key=lambda c: c.x).x, max(commands.commands, key=lambda c: c.x).x
	minY, maxY = min(commands.commands, key=lambda c: c.y).y, max(commands.commands, key=lambda c: c.y).y
	dx = maxX - minY
	dy = maxY - minY

	offset = (screensize[0] / 2 - scale * dx / 2, screensize[1] / 2 - scale * dy / 2)

	for command in commands.commands:
		command.x = (command.x - minX) * scale + offset[0]
		command.y = (command.y - minY) * scale + offset[1]


def main(args):
	if len(args) != 1:
		print("Usage: python path_to_points.py <svg_name>")
		sys.exit(1)

	SAMPLE_SIZE = 5
	SCALE = 2

	root = xml.etree.ElementTree.parse(args[0]).getroot()
	path_eles = list(root.iter("{http://www.w3.org/2000/svg}path"))

	if len(path_eles) == 0:
		print("Cannot find paths in file.")
		sys.exit(1)

	commands = Instructions()

	for ele in path_eles:
		toFill = True
		if "style" in ele.attrib:
			props =	{key: value for (key, value) in [style.split(":") for style in ele.attrib["style"].split(";")]}
			if "fill" in props and props["fill"] == "none":
				# should fill in paths
				toFill = False

		generateCommandsFromSVGPath(commands, ele.attrib["d"], toFill, SAMPLE_SIZE)

	normalizeCommands(commands, SCALE)

	print(Instructions.dumps(commands))


main(sys.argv[1:])