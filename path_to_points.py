# This files read an "input.svg".
# 
# python path_to_points.py | ~/Library/Android/sdk/tools/monkeyrunner ~/test_move.py

from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier, parse_path
import sys, json, sys, xml.etree.ElementTree

args = sys.argv[1:]
if len(args) != 1:
	print("Usage: python path_to_points.py <svg_name>")
	sys.exit(1)

root = xml.etree.ElementTree.parse(args[0]).getroot()
path_eles = root.iter("{http://www.w3.org/2000/svg}path")
path_ele = None

for ele in path_eles:
	path_ele = ele
	break

if path_ele is None:
	print("Cannot find input.svg")
	sys.exit(1)

path = parse_path(path_ele.attrib["d"])

output = []

prev_end_point = (-1-1j)
prev_end_point_x = -1
prev_end_point_y = -1
for line in path:
	(start, end) = line.start, line.end
	(start_x, start_y) = (start.real, start.imag)
	(end_x, end_y) = (end.real, end.imag)
	if prev_end_point != start:
		output.append({
			"mode": "UP",
			"x": prev_end_point_x,
			"y": prev_end_point_y
		})
		output.append({
			"mode": "DOWN",
			"x": start_x,
			"y": start_y
		})
	output.append({
		"mode": "MOVE",
		"x": end_x,
		"y": end_y
	})
	prev_end_point = end
	prev_end_point_x = end_x
	prev_end_point_y = end_y

output.append({
	"mode": "UP",
	"x": prev_end_point_x,
	"y": prev_end_point_y
})

print("|".join(["%s,%d,%d" % (instr["mode"], instr["x"], instr["y"]) for instr in output]))
