# ~/Library/Android/sdk/tools/bin/monkeyrunner print_path.py
import os, sys, ast
from instructions import Instructions
from com.android.monkeyrunner import MonkeyRunner, MonkeyImage, MonkeyDevice
import subprocess

def rewrite_line(string):
	sys.stdout.write("\r")
	sys.stdout.write(string)
	sys.stdout.flush()

def init_device():
	print("Waiting for connection to device...")
	device = MonkeyRunner.waitForConnection()
	print("Sending commands...")

	return {
		"device"	: device,
		"delay" 	: 0.00
	}

def actions(mode, x, y, **kwargs):
	device  	= kwargs["device"]
	delay   	= kwargs["delay"]
	progress	= kwargs["progress"]

	if mode == Instructions.DOWN:
		device.touch(x, y, MonkeyDevice.DOWN)
	elif mode == Instructions.MOVE:
		device.touch(x, y, MonkeyDevice.MOVE)
	elif mode == Instructions.UP:
		device.touch(x, y, MonkeyDevice.UP)
		MonkeyRunner.sleep(delay * 10)

	rewrite_line("Progress: %d%%" % (progress * 100))
	MonkeyRunner.sleep(delay)

def clean_up(**kwargs):
	rewrite_line("Completed.       \n")

def main(args):
	if len(args) != 1:
		print("Usage: ~/Library/Android/sdk/tools/bin/monkeyrunner print_path.py <svg_name>")
		sys.exit(1)


	# run svg parsing outside of Jython
	print("Parsing input svg...")
	process = subprocess.Popen(["python", "path_to_points.py", args[0]], stdout=subprocess.PIPE)
	stdout, stderr = process.communicate()

	if process.returncode != 0:
		sys.exit(process.returncode)

	commands = Instructions.loads(stdout)
	print("Received %d commands." % len(commands))

	commands.run(init_device, actions, clean_up)


main(sys.argv[1:])