import knewton.config
import copy
import urllib
import cStringIO
import json
import pycurl


PydutyConfigPath = knewton.config.ConfigPathDefaults([
	'', '~/.pyduty', '/etc/pyduty'])
PydutyConfig = knewton.config.ConfigDefault(config_path=PydutyConfigPath)

def get_api_key(filename='api'):
	confhash = PydutyConfig.fetch_config(filename)
	try:
		return confhash['api_key']
	except:
		raise KeyError('config file has no key "api_key"')

def get_domain(filename='api'):
	confhash = PydutyConfig.fetch_config(filename)
	try:
		return confhash['domain']
	except:
		raise KeyError('config file has no key "api_key"')

def list_get_func(key, domain, path, **kwargs):
	def retfunc(offset=0):
		c = pycurl.Curl()
		body_buf = cStringIO.StringIO()
		data = copy.copy(kwargs)
		data['offset'] = offset
		url = "https://%s/%s?%s" % (domain, path, urllib.urlencode(data))
		header = ['Content-type: application/json', 'Authorization: Token token=%s' % key]
		c.setopt(c.HTTPHEADER, header)
		c.setopt(c.URL, url)
		c.setopt(c.WRITEFUNCTION, body_buf.write)
		c.perform()
		jstring = body_buf.getvalue()
		return_code = c.getinfo(c.HTTP_CODE)
		if return_code != 200:
			raise Exception("Return code %s\n%s" % (return_code, jstring))
		return json.loads(jstring)
	return retfunc

class ListIterator:
	def __init__(self, func, fieldname):
		self.func = func
		self.fieldname = fieldname
		self.payload = None
		self.current = 0

	def __iter__(self):
		return self

	def next(self):
		if not self.payload:
			self.payload = self.func()
			self.current = 0
		limit = self.payload['limit']
		offset = self.payload['offset']
		total = self.payload['total']
		if self.current + offset >= total:
			raise StopIteration
		if self.current >= limit:
			newoffset = limit + offset
			self.payload = self.func(newoffset)
			self.current = 0
		self.current += 1
		return self.payload[self.fieldname][self.current - 1]

def get(key, domain, path, object_id, **kwargs):
	c = pycurl.Curl()
	body_buf = cStringIO.StringIO()
	url = "https://%s/%s/%s?%s" % (domain, path, object_id, urllib.urlencode(kwargs))
	header = ['Content-type: application/json', 'Authorization: Token token=%s' % key]
	c.setopt(c.HTTPHEADER, header)
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, body_buf.write)
	c.perform()
	jstring = body_buf.getvalue()
	return_code = c.getinfo(c.HTTP_CODE)
	if return_code != 200:
		raise Exception("Return code %s\n%s" % (return_code, jstring))
	return json.loads(jstring)

def post(key, domain, path, **kwargs):
	c = pycurl.Curl()
	body_buf = cStringIO.StringIO()
	url = "https://%s/%s" % (domain, path)
	header = ['Content-type: application/json', 'Authorization: Token token=%s' % key]
	c.setopt(c.HTTPHEADER, header)
	c.setopt(c.URL, url)
	c.setopt(c.POSTFIELDS, json.dumps(kwargs))
	c.setopt(c.WRITEFUNCTION, body_buf.write)
	c.perform()
	jstring = body_buf.getvalue()
	return_code = c.getinfo(c.HTTP_CODE)
	if return_code != 201:
		raise Exception("Return code %s\n%s" % (return_code, jstring))
	return json.loads(jstring)