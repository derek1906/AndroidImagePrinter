# This files read an "input.svg".
# 
# python path_to_points.py | ~/Library/Android/sdk/tools/monkeyrunner ~/test_move.py

from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier, parse_path
import sys, json, sys, xml.etree.ElementTree
import numpy as np
from instructions import Instructions

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

	return (lambda t: np.array([t**3, t**2, t, 1]).dot(cubic_bezier_matrix).dot(inputs))


def generateCommandsFromSVGPath(commands, path):
	path = parse_path(path)

	sample_size = 5

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
			commands.add(Instructions.MOVE, end[0], end[1])
		# CubicBezier
		elif isinstance(line, CubicBezier):
			# sample points
			curve_start = (line.start.real, line.start.imag)
			curve_ctrl1 = (line.control1.real, line.control1.imag)
			curve_ctrl2 = (line.control2.real, line.control2.imag)
			curve_end = (line.end.real, line.end.imag)
			curve = bezier_sample(curve_start, curve_ctrl1, curve_ctrl2, curve_end)

			for i in xrange(sample_size):
				t = float(i + 1) / float(sample_size)
				point = curve(t)
				commands.add(Instructions.MOVE, point[0], point[1])
		# QuadraticBezier
		elif isinstance(line, QuadraticBezier):
			curve_start = (line.start.real, line.start.imag)
			curve_ctrl = (line.control.real, line.control.imag)
			curve_end = (line.end.real, line.end.imag)
			curve = bezier_sample(curve_start, curve_ctrl, curve_ctrl, curve_end)

			for i in xrange(sample_size):
				t = float(i + 1) / float(sample_size)
				point = curve(t)
				commands.add(Instructions.MOVE, point[0], point[1])
		else:
			raise NotImplemented()

		prev_end = end

	# release touch
	commands.add(Instructions.UP, prev_end[0], prev_end[1])

	return commands


def main(args):
	if len(args) != 1:
		print("Usage: python path_to_points.py <svg_name>")
		sys.exit(1)

	root = xml.etree.ElementTree.parse(args[0]).getroot()
	path_eles = list(root.iter("{http://www.w3.org/2000/svg}path"))

	if len(path_eles) == 0:
		print("Cannot find paths in file.")
		sys.exit(1)

	commands = Instructions()

	for ele in path_eles:
		generateCommandsFromSVGPath(commands, ele.attrib["d"])
		if "style" in ele.attrib:
			props =	{key: value for (key, value) in [style.split(":") for style in ele.attrib["style"].split(";")]}
			if "fill" in props and props["fill"] != "none":
				pass

	print(Instructions.dumps(commands))


main(sys.argv[1:])