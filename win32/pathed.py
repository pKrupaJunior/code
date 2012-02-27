#!python
# pathed - a %PATH% editor for Windows, not entirely unlike ed

import os
import sys
import win32con as Con
from nullroute.windows.registry import RegistryKey
	
def display_buf():
	for i, item in enumerate(buf):
		print "%4d - %s" % (i, item)

def display_stack():
	for i, item in enumerate(stack):
		print "+ %s " % (item)

def display():
	display_buf()
	display_stack()

update = False

stack = []

ukey = RegistryKey(Con.HKEY_CURRENT_USER, "Environment")
upath, _utype = ukey["PATH"]
ubuf = upath.split(os.pathsep)

skey = RegistryKey(Con.HKEY_LOCAL_MACHINE,
	"System\\CurrentControlSet\\Control\\Session Manager\\Environment")
spath, _stype = skey["PATH"]
sbuf = spath.split(os.pathsep)

bufs = [ubuf, sbuf]
buf, bname = ubuf, "usr"

display()

while True:
	try:
		tokens = raw_input("pathed %s> " % bname).split()
	except EOFError:
		update = True
		break
	except KeyboardInterrupt:
		update = False
		break
	
	token = lambda: tokens.pop(0)
	
	try:
		cmd = token()
	except IndexError:
		cmd = None
	
	if cmd is None:
		display()

	elif cmd == "q":
		update = True
		break

	elif cmd == "x":
		update = False
		break

	elif cmd == "i":
		try:
			pos, arg = tokens
		except ValueError:
			pos = 0
			arg, = tokens
		else:
			pos = int(pos)
		buf.insert(pos, arg)

	elif cmd == "a":
		try:
			pos, arg = tokens
		except ValueError:
			pos = None
			arg, = tokens
		else:
			pos = int(pos)

		if pos is None:
			buf.append(arg)
		else:
			buf.insert(pos+1, arg)

	elif cmd == "d":
		pos, = tokens
		pos = int(pos)
		try:
			val = buf.pop(pos)
		except IndexError:
			print "out of range"
		else:
			stack.append(val)
			display_stack()

	elif cmd == "y":
		pos, = tokens
		pos = int(pos)
		val = buf[pos]
		stack.append(val)
		display_stack()

	elif cmd == "P":
		pos, = tokens
		pos = int(pos)

		try:
			val = stack.pop()
		except IndexError:
			print "stack empty"
		else:
			buf.insert(pos, val)
			display_stack()

	elif cmd == "p":
		pos, = tokens
		pos = int(pos)

		try:
			val = stack.pop()
		except IndexError:
			print "stack empty"
		else:
			buf.insert(pos+1, val)
			display_stack()

	elif cmd == "sw":
		a = int(token())
		b = int(token())
		buf[a], buf[b] = buf[b], buf[a]
		display_buf()

	elif cmd == "r":
		try:
			val = stack.pop()
		except IndexError:
			print "stack empty"
		else:
			stack.insert(0, val)
			display_stack()
		
	elif cmd == "pop":
		try:
			val = stack.pop()
		except IndexError:
			print "stack empty"
		else:
			display_stack()

	elif cmd == "/":
		if buf is ubuf:
			buf, bname = sbuf, "sys"
		else:
			buf, bname = ubuf, "usr"
		display_buf()

if update:
	print "Updating"
	ukey["PATH"] = os.pathsep.join(ubuf), _utype
	skey["PATH"] = os.pathsep.join(sbuf), _stype
else:
	print "Discarding changes"
