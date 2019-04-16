# setup Imports
from burp import IBurpExtender
from burp import IHttpListener
from burp import IHttpRequestResponse
from burp import IResponseInfo
from burp import IExtensionHelpers
import sys

# Class BurpExtender (Required) contaning all functions used to interact with Burp Suite API
class BurpExtender(IBurpExtender, IHttpListener):

    # define registerExtenderCallbacks: From IBurpExtender Interface
    def registerExtenderCallbacks(self, callbacks):

        # keep a reference to our callbacks object (Burp Extensibility Feature)
        self._callbacks = callbacks
        # obtain an extension helpers object (Burp Extensibility Feature)
        # http://portswigger.net/burp/extender/api/burp/IExtensionHelpers.html
        self._helpers = callbacks.getHelpers()
        # set our extension name that will display in Extender Tab
        self._callbacks.setExtensionName("API hmac")
        # register ourselves as an HTTP listener
        callbacks.registerHttpListener(self)

    # define processHttpMessage: From IHttpListener Interface
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if messageIsRequest and str(messageInfo.url).startswith('https://target.com:443/api'):
            import hashlib
            import time
            import hmac

            api_key = 'key'
            api_secret = 'secret'
            ts = int(time.time() * 1000)
            version = 1

            requestInfo = self._helpers.analyzeRequest(messageInfo)
            headers = requestInfo.getHeaders()
            originalBody = messageInfo.getRequest()[requestInfo.getBodyOffset():]
            msgBody = ''.join(chr(c) for c in originalBody)

            message = ':'.join([api_key, str(ts), str(version), msgBody])
            sign = hmac.new(api_secret, message, digestmod=hashlib.sha256).hexdigest()

            authorization = 'AUTH ' + ':'.join([api_key, str(ts), str(version), sign])

            headers.add('Authorization: ' + authorization)

            message = self._helpers.buildHttpMessage(headers, originalBody)
            print(self._helpers.bytesToString(message))

            messageInfo.setRequest(message)
