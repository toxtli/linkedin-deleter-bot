# python deleter.py -u [SEARCH_URL]

import sys
import json
import time
import getopt
import subprocess
from selenium import webdriver
from SeleniumHelper import SeleniumHelper

reload(sys)
sys.setdefaultencoding('utf8')

class LinkedinController(SeleniumHelper):

	LOGIN_USER_VALUE = 'ctoxtli@gmail.com'
	LOGIN_PASS_VALUE = 'hackool'
	LOGIN_USER_PATH_NORMAL = '#login-email'
	LOGIN_PASS_PATH_NORMAL = '#login-password'

	TIMEOUT = 20
	INITIAL_URL_NORMAL = 'https://www.linkedin.com/'
	SEARCH_BAR_PATH_NORMAL = '#main-search-box'

	SEARCH_URL_PAGE_NUMBER_NORMAL = '&page_num='
	USER_CONTAINER_PATH_NORMAL = '#results'
	USER_LIST_CONTAINER_PATH_NORMAL = '#results li.result'
	USER_NAME_PATH_NORMAL = 'div > h3 > a'
	USER_POSITION_PATH_NORMAL = 'div > dl.snippet > dd > p'
	USER_LOCATION_PATH_NORMAL = 'div > dl.demographic'
	USER_COMMON_PATH_NORMAL = 'div > div.related-wrapper.collapsed > ul > li.shared-conn > a'
	USER_DESCRIPTION_PATH_NORMAL = '.description'
	USER_IMAGE_PATH_NORMAL = 'a img'
	USER_URL_PATH_NORMAL = 'a'
	URL_DELETE = 'https://www.linkedin.com/profile/remove-from-network'

	data = {}
	token = ''
	baseUrl = ''
	criterias = ['president','vp','director','owner','founder','ceo','cto','sistemas','lead','desarroll','mobile','develop','software','hardware','firmware','programa','programm','engineer','ingeniero','partner','propietario','fundador','talent','recruit','head','recluta','tech','tecn','comput','empresario','empresaria','selecci','web','code','chief','entrepreneur','emprendedor','freelance','electro','bot','search','research','inve','human','socio','socia','data','datos','system','hack',' it',' ti','it ','ti ','rh ','hr ',' rh',' hr','founder','fund','rrhh','devops','técn','dueñ']
	contains = ['commercial','comercial']
	callback = None

	def login(self):
		self.loadPage(self.INITIAL_URL_NORMAL)
		self.waitAndWrite(self.LOGIN_USER_PATH_NORMAL, self.LOGIN_USER_VALUE)
		self.submitForm(self.selectAndWrite(self.LOGIN_PASS_PATH_NORMAL, self.LOGIN_PASS_VALUE))
		element = self.waitShowElement(self.SEARCH_BAR_PATH_NORMAL)

	def searchMorePeople(self, numPage):
		if not self.baseUrl:
			self.baseUrl = self.driver.current_url
			self.baseUrl = self.baseUrl.split(self.SEARCH_URL_PAGE_NUMBER_NORMAL)
			self.baseUrl = self.baseUrl.pop(0)
		start = (numPage - 1) * 25
		curUrl = self.baseUrl + self.SEARCH_URL_PAGE_NUMBER_NORMAL + str(numPage)
		self.loadPage(curUrl)

	def filterUser(self, description):
		if description:
			description = description.lower()
			for word in self.contains:
				if word in description:
					return False
			for word in self.criterias:
				if word in description:
					return True
		return False

	def filterAnalysis(self, containers):
		exit = []
		for element in containers:
			userData = {}
			username = self.getElementFromValue(element, self.USER_NAME_PATH_NORMAL)
			description = self.getElementFromValue(element, self.USER_DESCRIPTION_PATH_NORMAL)
			userElegible = self.filterUser(description)
			connId = element.get_attribute('data-li-entity-id')
			if connId:
				urlUser = self.getElementFromAttribute(element, self.USER_NAME_PATH_NORMAL, 'href')
				urlDelete = self.URL_DELETE + '?id=' + connId + '&csrfToken=' + str(self.token)
				if not userElegible:
					exit.append({
						"id": connId,
						"username":username,
						"description":description,
						"userElegible":userElegible,
						"urlUser": urlUser,
						"urlDelete": urlDelete
				})
		for user in exit:
			print user['description']
			print user['urlUser']
			self.loadPage(user['urlDelete'])
		return exit

	def extractUsers(self):
		container = self.waitShowElement(self.USER_CONTAINER_PATH_NORMAL)
		containers = self.getElements(self.USER_LIST_CONTAINER_PATH_NORMAL)
		return self.callback(containers)

	def getToken(self):
		html = self.driver.page_source
		self.token = self.getCharsFrom(html, 'csrfToken=', 26)
		print self.token

	def saveToFile(self, fileName, data):
		file_ = open(fileName, 'w')
		content = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
		file_.write(content)
		file_.close()

	def startWithUrl(self, callback, url, fromPage=1, toPage=1):
		print 'Logging in'
		results = []
		self.callback = callback
		self.login()
		self.getToken()
		self.loadPage(url)
		toPage = toPage + 1
		for numPage in range(fromPage, toPage):
			print 'Searching people ' + str(numPage)
			self.searchMorePeople(numPage)
			print 'Extracting users'
			results += self.extractUsers()
			print 'Users extracted: ' + str(len(results))
		self.saveToFile('deleter.json', results)
		self.close()
		return results

	def __init__(self): 
		self.driver = webdriver.Firefox()
		# self.driver = webdriver.PhantomJS()
		self.driver.set_page_load_timeout(self.TIMEOUT)

def main(argv):
	fromPage = 1
	toPage = 100
	url = ''
	opts, args = getopt.getopt(argv, "f:t:u:")
	if opts:
		for o, a in opts:
			if o in ("-f"):
				fromPage = int(a)
			elif o in ("-t"):
				toPage = int(a)
			elif o in ("-u"):
				url = a
	linkedin = LinkedinController()
	print "Process started"
	linkedin.startWithUrl(linkedin.filterAnalysis, url=url, fromPage=fromPage, toPage=toPage)
	print "Process ended"

if __name__ == "__main__":
    main(sys.argv[1:])