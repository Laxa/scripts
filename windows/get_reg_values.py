#!/usr/bin/env python

from impacket.winregistry import Registry, REG_SZ, REG_EXPAND_SZ, REG_BINARY, REG_DWORD, REG_MULTISZ
from sys import stderr, exit
from os.path import exists
from argparse import ArgumentParser

MAX_INT = 0x100000
REG_TYPE = {
	1: "REG_SZ",
	2: "REG_EXPAND_SZ",
	3: "REG_BINARY",
	4: "REG_DWORD",
	7: "REG_MULTISZ",
	11: "REG_QWORD"
}


def reg_convert(reg_type, reg_val):
	if reg_type == REG_SZ or reg_type == REG_EXPAND_SZ:
		if isinstance(reg_val, int):
			return str(reg_val)
		else:
			return reg_val.decode("utf-16")[:-1]
	elif reg_type == REG_BINARY:
		return reg_val
	elif reg_type == REG_DWORD:
		return int(reg_val)
	elif reg_type == REG_MULTISZ:
		if isinstance(reg_val, int):
			return str(reg_val)
		else:
			return ",".join(reg_val.decode("utf-16")[:-2].split("\x00"))


def browse_values(reg, key, depth=0):
	for value in reg.enumValues(reg.findKey(key)):
		try:
			reg_data = reg.getValue(key + "\\" + value)
			if reg_data is not None:
				reg_type, reg_val = reg_data
				try:
					print(u"{pad}{:40} -> {:15} {}".format(value, "[{}]".format(REG_TYPE[reg_type]), reg_val, pad=depth * ' '))
				except UnicodeDecodeError:
					print(u"{pad}{:40} -> {:15} {}".format(
						value, "[{}]".format(REG_TYPE[reg_type]), reg_val.__repr__(), pad=depth * ' '))
		except KeyError:
			pass


def browse_key(reg, root, max_depth=0, depth=0):
	print("{pad}> {}".format(root, pad=depth * ' '))
	if max_depth != 0:
		browse_values(reg, root, depth + 4)
	if max_depth != 0:
		for key in reg.enumKey(reg.findKey(root)):
			browse_key(reg, root + "\\" + key, max_depth - 1, depth + 2)


def main():
	epilog = 'Example use: get_reg_values.py -d 1 \'\\CurrentControlSet\Control\Lsa\' SYSTEM'
	parser = ArgumentParser(epilog=epilog)
	parser.add_argument("-d", "--depth", type=int, help="depth of the browsing")
	parser.add_argument("key", help="Key from which run the browsing")
	parser.add_argument("hive", help="Hive file to browse")
	parser
	args = parser.parse_args()

	key = args.key
	hive = args.hive
	if args.depth is not None:
		max_depth = args.depth
	else:
		max_depth = MAX_INT

	if not exists(hive):
		stderr.write("[!] {} does not exist\n".format(hive))
		exit(2)

	reg = Registry(hive)
	try:
		root = reg.findKey(key)
		if root is None:
			path = key.split("\\")
			path.pop(0)
			while root is None and path != []:
				root = reg.findKey("\\".join(path))
				path.pop(0)
			if root is None:
				stderr.write("[!] {} not found in hive {}\n".format(key, hive))
				exit(3)
			prefix = "\\".join(path)
		else:
			prefix = key
	except Exception as e:
		if e.message == "HashRecords":
			if reg.enumKey(reg.rootKey) == []:
				stderr.write("[!] {} is empty\n".format(hive))
			else:
				stderr.write("[!] {}\n".format(e.message))
		else:
			stderr.write("[!] {}\n".format(e.message))
		exit(4)

	print(u"[*] {}:{}".format(hive, key))
	browse_values(reg, prefix)
	for key in reg.enumKey(reg.findKey(prefix)):
		browse_key(reg, prefix + "\\" + key, max_depth, 2)

if __name__ == "__main__":
	main()
