if not messageIsRequest and str(messageInfo.url).startswith('https://toto.com:443/api/users/rights'):
	# la reponse contient les headers
    resp = messageInfo.getResponse()
    resp = ''.join(chr(c) for c in resp)
	# on cherche la position des donnees
    pos = resp.find('\n\r\n')
    if pos != -1:
		# on reinjecte les headers dans la reponse
        resp = resp[:pos+3]
        p = 'remplacement du content de la request'
		# on remplace le contenu original de la reponse
        resp += p
        import re
		# on mets a jour le content-length
        resp = re.sub('Content-Length: \d+', 'Content-Length: ' + str(len(p)), resp)
        messageInfo.setResponse(resp)
