# python batch.py -i ../../data/linkedin-delete.json -c ../../config/linkedin-config.txt -f 1

import sys
import time
import getopt
import getpass
import simplejson
import subprocess
import ConfigParser
from selenium import webdriver
from SeleniumHelper import SeleniumHelper

reload(sys)  
sys.setdefaultencoding('utf8')

class LinkedinController(SeleniumHelper):

	LOGIN_USER_VALUE = ''
	LOGIN_PASS_VALUE = ''
	LOGIN_USER_PATH_NORMAL = '#login-email'
	LOGIN_PASS_PATH_NORMAL = '#login-password'

	TIMEOUT = 20
	INITIAL_URL_NORMAL = 'https://www.linkedin.com/'
	SEARCH_BAR_PATH_NORMAL = '#main-search-box'
	DIV_LOADED = 'body'
	DIV_PROFILE = '#top-card'

	URL_DELETE = 'https://www.linkedin.com/profile/remove-from-network'

	data = {}
	token = ''
	waitTime = 3600

	def login(self):
		self.loadPage(self.INITIAL_URL_NORMAL)
		self.waitAndWrite(self.LOGIN_USER_PATH_NORMAL, self.LOGIN_USER_VALUE)
		self.submitForm(self.selectAndWrite(self.LOGIN_PASS_PATH_NORMAL, self.LOGIN_PASS_VALUE))
		element = self.waitShowElement(self.SEARCH_BAR_PATH_NORMAL)

	def getConnId(self):
		connId = ''
		html = self.driver.page_source
		arr1 = html.split('connId=')
		if len(arr1) > 1:
			arr2 = arr1[1].split('&')
			connId = arr2[0]
		return connId

	def deleteUser(self, containers):
		connId = self.getConnId()
		if connId:
			urlDelete = self.URL_DELETE + '?id=' + connId + '&csrfToken=' + str(self.token)
			self.loadPage(urlDelete)
			print 'User deleted'
		else:
			print 'User is not a connection'

	def getToken(self):
		html = self.driver.page_source
		self.token = self.getCharsFrom(html, 'csrfToken=', 26)
		print self.token

	def getCredentials(self, filename):
		config = ConfigParser.ConfigParser()
		config.read(filename)
		self.LOGIN_USER_VALUE = config.get('credentials', 'login_user_value')
		self.LOGIN_PASS_VALUE = config.get('credentials', 'login_pass_value')

	def askCredentials(self):
		self.LOGIN_USER_VALUE = raw_input('Username: ')
		self.LOGIN_PASS_VALUE = getpass.getpass('Password: ')

	def startWithFile(self, callbacks, inputFile, fromPage, toPage, credentials=None):
		try:
			urls = simplejson.loads(open(inputFile).read())
			numElements = len(urls)
		except:
			numElements = 0	
		if numElements > 0:
			if toPage == -1:
				toPage = numElements
			else:
				if toPage > numElements:
					toPage = numElements
			if fromPage < numElements:
				fromPage -= 1
				if credentials:
					self.getCredentials(credentials)
				else:
					self.askCredentials()
				self.driver = webdriver.Firefox()
				# self.driver = webdriver.PhantomJS()
				self.driver.set_page_load_timeout(self.TIMEOUT)
				print 'Logging in'
				self.login()
				self.getToken()
				for numPage in range(fromPage, toPage):
					url = urls[numPage]
					self.loadPage(url)
					self.waitShowElement(self.DIV_LOADED)
					attemp = 0
					while not self.getElement(self.DIV_PROFILE):
						attemp += 1
						print 'Attemp: ' + str(attemp)
						print 'Blocked page shown'
						print 'Waiting ' + str(self.waitTime) + ' seconds'
						time.sleep(self.waitTime)
						self.loadPage(url)
						self.waitShowElement(self.DIV_LOADED)
					print 'Processing user ' + str(numPage) + ' ' + url
					for callback in callbacks:
						callback(url)
					print 'NEXT'
				self.close()
			else:
				print 'Index out of bounds'
		else:
			print 'Data could not be extracted'

	def __init__(self): 
		pass

def main(argv):
	fromPage = 1
	toPage = -1
	inputFile = ''
	credentials = ''
	opts, args = getopt.getopt(argv, "f:t:i:c:")
	if opts:
		for o, a in opts:
			if o in ("-f"):
				fromPage = int(a)
			elif o in ("-t"):
				toPage = int(a)
			elif o in ("-i"):
				inputFile = a
			elif o in ("-c"):
				credentials = a
	if inputFile:
		linkedin = LinkedinController()
		print "Process started"
		linkedin.startWithFile([linkedin.deleteUser], inputFile=inputFile, fromPage=fromPage, toPage=toPage, credentials=credentials)
		print "Process ended"
	else:
		print 'No input file was detected'

if __name__ == "__main__":
    main(sys.argv[1:])