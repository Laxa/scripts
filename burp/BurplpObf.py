from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator

# Extension specific
import ipobf

class IntruderPayloadGenerator(IIntruderPayloadGenerator):
    
    mutations = []
    index = 0

    def hasMorePayloads(self):

        if (self.index == 0):
            # print("New run")
            return True
        elif self.mutations and len(self.mutations) > self.index:
            # print("Going ahead [%d/%d]" % (self.index, len(self.mutations)))
            return True
        else:
            # print("No mutations left!")
            return False

    def getNextPayload(self, baseValue):

        # Debug
        # import pdb; pdb.set_trace()
        
        # Generate mutations if needed
        if not self.mutations:

            # baseValue is an array of bytes, value is None if mode = "Battering ram"
            if baseValue is None:
                default_ip = "127.0.0.1"
                print("Battering ram mode? Using default base value...")
                ip = default_ip
            else:
                ip = baseValue.tostring()

            # Generate mutations
            self.mutations = ipobf.generate_mutations(ipobf.parse_ip(ip))
            print("Base value is '%s'" % ip)
            print("Mutations generated: %d" % len(self.mutations))

        # Get the current item
        cur = self.mutations[self.index]
        self.index = self.index + 1

        # Return it
        return cur

    def reset(self):
        self.mutations = []
        self.index = 0

class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):

    def	registerExtenderCallbacks(self, callbacks):

        # Obtain an extension helpers object
        self._helpers = callbacks.getHelpers()

        # Set our extension name
        callbacks.setExtensionName("IP obfuscator")

        # Register as a payload generator
        callbacks.registerIntruderPayloadGeneratorFactory(self)

        return

    def getGeneratorName(self) :

        return "Obfuscated IP addresses"

    def createNewInstance(self, attack):

        return IntruderPayloadGenerator()

