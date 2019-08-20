#!/usr/bin/python

import sys, copy

###########################
######## FUNCTIONS ########
###########################

def parse_ip(ip_as_str):

	try:
		ip = map(int, ip_as_str.split('.'))
	except:
		raise RuntimeError('Invalid parameter')
    
	if len(ip) == 4 and all((d >= 0 and d <= 255) for d in ip):
		return ip
	else:
		raise RuntimeError('Invalid parameter')

def base36encode(number):

    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'

    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36 or alphabet[0]

def generate_mutations(ip):

	m = []

	# Dotted decimal
	m.append(as_dotted_decimal(ip))
	m.append(as_dotted_decimal(ip, 'overflow'))

	# Integer
	m.append(str(as_integer(ip)))
	m.append(str(as_integer(ip, 'overflow')))

	# Octal
	m.append(as_octal(ip))
	m.append(as_octal(ip, 'zeros'))

	# Hexadecimal
	m.append(as_hex(ip))
	m.append(as_hex(ip, 'dotless'))
	m.append(as_hex(ip, 'dotless_garbage'))

	# xip.io
	m.append(as_xip(ip))
	m.append(as_xip(ip, 'base36'))

	# IPv6
	m.append(as_mapped_ipv6(ip))
	m.append(as_mapped_ipv6(ip, 'hex'))
	m.append(as_compatible_ipv6(ip))
	m.append(as_compatible_ipv6(ip, 'hex'))

	# Mix the formats
	m.append(as_mix(ip, 'dohp'))
	m.append(as_mix(ip, 'hodd'))
	m.append(as_mix(ip, 'd3i'))
	m.append(as_mix(ip, 'od2i'))

	# Special cases for localhost
	if ip[0] == 127:
		m.append('127.127.127.127') # Yes, it's a /8
		m.append('0.0.0.0')
		m.append('[::1]')
		m.append('[::]')

	return m

def as_dotted_decimal(dec, fmt='normal'):

	if fmt == 'overflow':
		dec = copy.deepcopy(dec)
		for i in xrange(len(dec)):
			dec[i] = dec[i] + 256

	return '.'.join(map(str, dec))

def as_integer(dec, fmt='normal'):

	integer = reduce(lambda a,b: a<<8 | b, dec)

	if fmt == 'overflow':
		return integer + 256**4
	else:
		return integer

def as_octal(dec, fmt='normal'):

	if fmt == 'zeros':
		return '.'.join(format(d, '08o') for d in dec)
	else:
		return '.'.join('0' + format(d, 'o') for d in dec)

def as_hex(dec, fmt='normal'):

	if fmt == 'dotless':
		return '0x' + ''.join(format(d, '02x') for d in dec)
	elif fmt == 'dotless_garbage':
		return '0x' + '31337' + ''.join(format(d, '02x') for d in dec)
	else:
		return '.'.join(map(hex, dec))

def as_xip(dec, fmt='normal'):

	garbage = '41.42.666.31337' + '.'
	xip = '.' + 'xip.io'

	if fmt == 'base36':
		# Reverse the IP, convert as integer then as base36
		return garbage + base36encode(as_integer(dec[::-1])) + xip
	else:
		return garbage + as_dotted_decimal(dec) + xip

def as_mapped_ipv6(dec, fmt='normal'):

	if fmt == 'hex':
		mapped = ''.join(format(d, '02x') for d in dec[:2]) + ':' + ''.join(format(d, '02x') for d in dec[2:])
	else:
		mapped = as_dotted_decimal(dec)

	return '[::ffff:' + mapped + ']'

def as_compatible_ipv6(dec, fmt='normal'):

	if fmt == 'hex':
		compat = ''.join(format(d, '02x') for d in dec[:2]) + ':' + ''.join(format(d, '02x') for d in dec[2:])
	else:
		compat = as_dotted_decimal(dec)

	return '[::' + compat + ']'

def as_mix(dec, fmt):
	
	d = []

	if fmt == 'hodd':
		# Hex + Oct + Dec + Dec
		d.append('0x' + format(dec[0], '02x'))
		d.append('0' + format(dec[1], '02o'))
		d.append(dec[2])
		d.append(dec[3])
	elif fmt == 'dohp':
		# Dec + Oct + Hex + Padded_Oct
		d.append(dec[0])
		d.append('0' + format(dec[1], '02o'))
		d.append('0x' + format(dec[2], '02x'))
		d.append('000000' + format(dec[3], '02o'))
	elif fmt == 'd3i':
		# Dec + (Int * 3)
		d.append(dec[0])
		d.append(as_integer(dec[1:]))
	elif fmt == 'od2i':
		# Oct + Dec + (Int * 2)
		d.append('0' + format(dec[0], '02o'))
		d.append(dec[1])
		d.append(as_integer(dec[2:]))
		
	return '.'.join(map(str,d))

###########################
######## MAIN CODE ########
###########################

if __name__ == '__main__':

    # Returns an array of 4 decimal numbers
    ip = parse_ip(sys.argv[1])

    # Generate and print mutations
    for m in generate_mutations(ip):
        print(m)
