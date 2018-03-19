#!/usr/bin/env python2

from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer
import sys

class SimpleSecureCookieSessionInterface(SecureCookieSessionInterface):
	# Override method
	# Take secret_key instead of an instance of a Flask app
	def get_signing_serializer(self, secret_key):
		if not secret_key:
			return None
		signer_kwargs = dict(
			key_derivation=self.key_derivation,
			digest_method=self.digest_method
		)
		return URLSafeTimedSerializer(secret_key, salt=self.salt,
									  serializer=self.serializer,
									  signer_kwargs=signer_kwargs)

def decodeFlaskCookie(secret_key, cookieValue):
	sscsi = SimpleSecureCookieSessionInterface()
	signingSerializer = sscsi.get_signing_serializer(secret_key)
	return signingSerializer.loads(cookieValue)

# Keep in mind that flask uses unicode strings for the
# dictionary keys
def encodeFlaskCookie(secret_key, cookieDict):
	sscsi = SimpleSecureCookieSessionInterface()
	signingSerializer = sscsi.get_signing_serializer(secret_key)
	return signingSerializer.dumps(cookieDict)

if __name__=='__main__':
	sk = 'secret'
	sessionDict = {u'csrf_token':u'c6584ddca2670f834a5d39f782ae1220086db055', u'_fresh':True, u'user_id':
	u'XXXX',u'_id':u'XXX'}
	cookie = encodeFlaskCookie(sk, sessionDict)
	print cookie
	decodedDict = decodeFlaskCookie(sk, cookie)
	print decodedDict
