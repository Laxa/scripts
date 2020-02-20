#!/usr/bin/env python

import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data')
    o = parser.parse_args()
    decrypt=lambda x:''.join([chr(int(x[i:i+2],16)^ord('dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87'[(int(x[:2])+i/2-1)%53]))for i in range(2,len(x),2)])
    print(decrypt(o.data))

if __name__ == "__main__":
    main()
