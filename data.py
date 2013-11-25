#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import requests0 as requests
#import requests  
import json  
import sys
import urllib
import urllib2
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import string
import time
import re
import markup
import encodings
from os.path import basename
from urlparse import urlsplit
from selenium.common.exceptions import NoSuchElementException
from xgoogle.search import GoogleSearch, SearchError
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize
import networkx as nx
import matplotlib.pyplot as plt
from facepy.utils import get_extended_access_token
from facepy import GraphAPI
from random import randint



#https://developers.facebook.com/docs/reference/api/search/
#https://developers.facebook.com/tools/access_token/
#https://code.google.com/apis/console/b/0/?pli=1#project:48954835397:access
#https://code.google.com/apis/console/b/0/?pli=1#project:1048522442453:access

#Linkedin id
linke = "electr0sm0g.user@gmail.com"
#Linkedin password
passlinke = "lenovo"

#Clef Google API eet idcse
api_key = 'AIzaSyD0Fu6ww5U-A-9GqxokcymF0mWWKUHC58U' 
idcse = '003779372669635671735:v2e-sksoimg'

keyword2 = "fablab"

#FB token API
token = 'CAAH71Iw4WcoBAGNt50Y1vBZCi25bkHWRWJGWmc9aBga8o1fITWlVYJ4VimismlyHpoYZBuvPpUepIGAgxZCiL7G9cnY6Ps2iGtTYhBGyDy37ZAzlqsEAgKaZCUy6PZCZAhnSutbjZAodWfUqx3nEgZCj698gOGQkrZAxBXxHRxTA3JxgZDZD'
application_id = "558365280852426"
application_secret_key = "d2295d320c4fc00009989ab5628d627f"

repertoire_tmp = "/home/casi0/Bureau/OSINT/"

PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()
Title = "Data-mining OSINT "+keyword2
pageinfo = "OSINT"

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Bold',16)
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch,"First Page / %s" % pageinfo)
    canvas.restoreState()
    
def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch,"Page %d %s" % (doc.page, pageinfo))
    canvas.restoreState()

def google(mot): 

	Story.append(Spacer(1,0.2*inch))
	bogustext = ("Recherche google sur: "+mot)
	p = Paragraph(bogustext, style)
	Story.append(p)
	Story.append(Spacer(1,0.2*inch))
	try:
		gs = GoogleSearch(mot)
		gs.results_per_page = 5
		results = gs.get_results()
		for res in results:
			print res.title.encode('utf8')
			print res.desc.encode('utf8')
			print res.url.encode('utf8')
			bogustext = res.title.encode('utf8')
			p = Paragraph(bogustext, style)
			Story.append(p)
			bogustext = res.desc.encode('utf8')
			p = Paragraph(bogustext, style)
			Story.append(p)
			bogustext = res.url.encode('utf8')
			p = Paragraph(bogustext, style)
			Story.append(p)
			Story.append(Spacer(1,0.2*inch))
	except SearchError, e:
		print "Search failed: %s" % e
	
def url2name(url):
    return basename(urlsplit(url)[2])

#Fonction qui download un fichier a partir de son url
def download(url, localFileName = None):
	try:
		localName = url2name(url)
		req = urllib2.Request(url)
		r = urllib2.urlopen(req)
		if r.info().has_key('Content-Disposition'):
			# If the response has Content-Disposition, we take file name from it
			localName = r.info()['Content-Disposition'].split('filename=')[1]
			if localName[0] == '"' or localName[0] == "'":
				localName = localName[1:-1]
		elif r.url != url: 
			# if we were redirected, the real file name we take from the final URL
			localName = url2name(r.url)
		if localFileName: 
			# we can force to save the file as specified name
			localName = localFileName
		f = open(localName, 'wb')
		f.write(r.read())
		f.close()
		return "OK"
	except:
		return "KO"

def check_exists(word):
    try:
        driver.find_element_by_class_name(word)
    except NoSuchElementException:
        return False
    return True

#Fonction qui effectue un reverse image google a partir d'un fichier et insertion dans rapport.
def google_reverse(path):
	driver1 = webdriver.Firefox()
	driver1.get("http://images.google.fr")
	driver1.find_element_by_id("qbi").click()
	driver1.find_element_by_link_text("Importer une image").click()
	element = driver1.find_element_by_id("qbfile")
	element.send_keys(path)
	driver1.find_element_by_name("btnG").click()
	nom = driver1.find_element_by_id("lst-ib")
	driver1.close()
	element_text = nom.text
	element_attribute_value = nom.get_attribute('value')
	nom = element_attribute_value
	if nom != '':
		print "Nom trouve a partir de google reverse: "+nom 
		bogustext = "Nom suite a une recherche sur google image en reverse: "+nom 
		p = Paragraph(bogustext, style)
		Story.append(p)
		im = Image(path, 2*inch, 2*inch)
		Story.append(im)
		Story.append(Spacer(1,0.2*inch))
		Story.append(Spacer(1,0.2*inch))
		return nom
	return ''

#Fonction qui effectue un dork google contenant le mot clef sur linkedin. 
#Recherche profil, groups, company, titre sur linkedin et insertion de photo si trouvée dans rapport.
def linkedin_google_api(mot):
	
	#url = 'https://www.googleapis.com/customsearch/v1?key='+ api_key +'&cx='+ idcse +'&q=' + urllib.quote('site:linkedin.com intitle:" | Linkedin" "'+mot+'" -intitle:profiles -inurl:groups -inurl:company -inurl:title')#+'&start='+str(x)
	#response = requests.get(url)
	#print  json.dumps(response.json, indent=4)
	
	bogustext = 'Recherche de comptes Linkedin associees a la recherche '+keyword2+':'
	p = Paragraph(bogustext, style)
	Story.append(p)
	Story.append(Spacer(1,0.2*inch))
	compteur = 1
	 
	compt = 0
	v = 1
	w = 1
	while compt == 0:
		url = 'https://www.googleapis.com/customsearch/v1?key='+ api_key +'&cx='+ idcse +'&q=' + urllib.quote('site:linkedin.com intitle:" | Linkedin" "'+mot+'" -intitle:profiles -inurl:groups -inurl:company -inurl:title')+'&start='+str(v)
		response = requests.get(url)
		print  json.dumps(response.json, indent=4)
		if 'items' in response.json:
			for item in response.json['items']:
					if 'pagemap' in item:
						if 'nextPage' in response.json['queries']: 
							compt = 0
							v = str(response.json['queries']['nextPage'][0]['startIndex'])
						else:
							compt = 1
						if 'hcard' in item['pagemap']:
							hcard = item['pagemap']['hcard']  
							affiliations = []  
							name = 'N/A'  
							photo_url = 'N/A'  
							position = 'N/A'  
							company = 'N/A'  
							#location = item['pagemap']['person'][0]['location']  
							profile_url = item['formattedUrl']  
							for card in hcard:  
								if 'title' in card:
									if 'fn' in card: name = card['fn']
									G.add_edge(name,card["fn"])
							# If we are in our main contact info card  
								if 'title' in card:  
									if 'fn' in card: name = card['fn']  
									if 'photo' in card: 
											photo_url = card['photo'] 
											print photo_url
											try:
												w = random_with_N_digits(4)
												download(photo_url, repertoire_tmp+('w'+str(w))+'.jpg') 
												time.sleep(2)
												# Add an image
												img = 'w'+str(w)+'.jpg'
												path_img = repertoire_tmp+img
												bogustext = 'Photo: '
												p = Paragraph(bogustext, style)
												Story.append(p)
												im = Image(img, 2*inch, 2*inch)
												Story.append(im)
												compteur += 1 
												w += 1
											except:
												compteur += 1 
												w += 1
									company = card['title'] 
									G.add_edge(company,card['title'])
								affiliations.append(card['fn']) 
							Story.append(Spacer(1,0.2*inch))
							bogustext = 'Nom: ' + name
							p = Paragraph(bogustext, style)
							Story.append(p)
							#bogustext = 'Photo: '
							#p = Paragraph(bogustext, style)
							#Story.append(p)
							#im = Image(img, 2*inch, 2*inch)
							#Story.append(im)
							bogustext = 'Societe: ' + company
							p = Paragraph(bogustext, style)
							Story.append(p)
							bogustext = 'Profile: ' + profile_url
							p = Paragraph(bogustext, style)
							Story.append(p)
							Story.append(Spacer(1,0.2*inch))
							if name == 'N/A':
								print ''
							else:
								nom_url = name.encode('utf8')
								print nom_url
								google(nom_url)   
								if facebook_nom(nom_url) == "KO":
									break
								else:
									Story.append(Spacer(1,0.2*inch))
				
					elif 'kind' in item['pagemap']:  
							if 'nextPage' in response.json['queries']: 
								compt = 0
								v = str(response.json['queries']['nextPage'][0]['startIndex'])
							else:
								compt = 1
							affiliations = []  
							name = 'N/A'  
							photo_url = 'N/A'  
							position = 'N/A'  
							company = 'N/A' 
							if 'title' in item: name = item['title'].split(' - ')[0]
							poste = item['snippet'] 
							profile = item['link']
							bogustext = 'Recherche des comptes Linkedin associes a la recherche '+keyword2+'.'
							p = Paragraph(bogustext, style)
							Story.append(p)
							bogustext = 'Nom: ' + name
							G.add_edge(name,item['title'].split(' - ')[0])
							p = Paragraph(bogustext, style)
							Story.append(p)
							bogustext = 'Poste: ' + poste
							G.add_edge(poste,poste)
							p = Paragraph(bogustext, style)
							Story.append(p)
							bogustext = 'Profile: ' + profile
							p = Paragraph(bogustext, style)
							Story.append(p)
							Story.append(Spacer(1,0.2*inch))
							if name == 'N/A':
								print ''
							else:
								nom_url = name.encode('utf8')
								print nom_url
								google(nom_url)   
								if facebook_nom(nom_url) == "KO":
									break
								else:
									Story.append(Spacer(1,0.2*inch))
		else:
			compt = 1
			
#Fonction qui effectue un dork google contenant le mot clef sur linkedin. 
#Recherche profil, groups, company, titre sur linkedin et insertion de photo si trouvée dans rapport.
def linkedin_nom(mot):
	try:	
		#url = 'https://www.googleapis.com/customsearch/v1?key='+ api_key +'&cx='+ idcse +'&q=' + urllib.quote('site:linkedin.com intitle:" | Linkedin" "'+mot+'" -intitle:profiles -inurl:groups -inurl:company -inurl:title')#+'&start='+str(x)
		#response = requests.get(url)
		#print  json.dumps(response.json, indent=4)
	
		bogustext = 'Recherche de comptes Linkedin associees a la recherche '+mot+':'
		p = Paragraph(bogustext, style)
		Story.append(p)
		Story.append(Spacer(1,0.2*inch))
		compteur = 1
	 
		compt = 0
		v = 1
		w = 1
		while compt == 0:
		#while y < 10:
			#y += 1
			url = 'https://www.googleapis.com/customsearch/v1?key='+ api_key +'&cx='+ idcse +'&q=' + urllib.quote('site:linkedin.com intitle:" | Linkedin" "'+mot+'" -intitle:profiles -inurl:groups -inurl:company -inurl:title')+'&start='+str(v)
			response = requests.get(url)
			print  json.dumps(response.json, indent=4)
			if 'items' in response.json:
				for item in response.json['items']:
						if 'pagemap' in item:
							if 'nextPage' in response.json['queries']: 
								compt = 0
								v = str(response.json['queries']['nextPage'][0]['startIndex'])
							else:
								compt = 1
							if 'hcard' in item['pagemap']:
								hcard = item['pagemap']['hcard']  
								affiliations = []  
								name = 'N/A'  
								photo_url = 'N/A'  
								position = 'N/A'  
								company = 'N/A'  
								#location = item['pagemap']['person'][0]['location']  
								profile_url = item['formattedUrl']  
								for card in hcard:  
									if 'title' in card:
										if 'fn' in card: name = card['fn']
									G.add_edge(name,card["fn"])
								# If we are in our main contact info card  
									if 'title' in card:  
										if 'fn' in card: name = card['fn']  
										if 'photo' in card: 
												photo_url = card['photo'] 
												print photo_url
												try:
													w = random_with_N_digits(4)
													download(photo_url, repertoire_tmp+'z'+(str(w))+'.jpg') 
													time.sleep(2)
													# Add an image
													img = 'z'+str(w)+'.jpg'
													path_img = repertoire_tmp+img
													bogustext = 'Photo: '
													p = Paragraph(bogustext, style)
													Story.append(p)
													im = Image(img, 2*inch, 2*inch)
													Story.append(im)
													compteur += 1  
													w += 1
												except:
													compteur += 1
													w += 1
										company = card['title'] 
										#G.add_edge(company,card['title'])
									affiliations.append(card['fn']) 
								Story.append(Spacer(1,0.2*inch))
								bogustext = 'Nom: ' + name
								p = Paragraph(bogustext, style)
								Story.append(p)
								#bogustext = 'Photo: '
								#p = Paragraph(bogustext, style)
								#Story.append(p)
								#im = Image(img, 2*inch, 2*inch)
								#Story.append(im)
								bogustext = 'Societe: ' + company
								p = Paragraph(bogustext, style)
								Story.append(p)
								bogustext = 'Profile: ' + profile_url
								p = Paragraph(bogustext, style)
								Story.append(p)
								Story.append(Spacer(1,0.2*inch))
								#if name == 'N/A':
								#	print ''
								#else:
								#	facebook_nom(name)
								#	google(name)
								#	Story.append(Spacer(1,0.2*inch))
				
						elif 'kind' in item['pagemap']:  
								if 'nextPage' in response.json['queries']: 
									compt = 0
									v = str(response.json['queries']['nextPage'][0]['startIndex'])
								else:
									compt = 1
								affiliations = []  
								name = 'N/A'  
								photo_url = 'N/A'  
								position = 'N/A'  
								company = 'N/A' 
								if 'title' in item: name = item['title'].split(' - ')[0]
								poste = item['snippet'] 
								profile = item['link']
								bogustext = 'Recherche des comptes Linkedin associes a la recherche '+keyword2+'.'
								p = Paragraph(bogustext, style)
								Story.append(p)
								bogustext = 'Nom: ' + name
								G.add_edge(name,item['title'].split(' - ')[0])
								p = Paragraph(bogustext, style)
								Story.append(p)
								bogustext = 'Poste: ' + poste
								G.add_edge(poste,poste)
								p = Paragraph(bogustext, style)
								Story.append(p)
								bogustext = 'Profile: ' + profile
								p = Paragraph(bogustext, style)
								Story.append(p)
								Story.append(Spacer(1,0.2*inch))
								#if name == 'N/A':
								#	print ''
								#else:
								#	facebook_nom(name)
								#	google(name)
								#	Story.append(Spacer(1,0.2*inch))
			else:
				compt = 1
		return "OK"
	except:
		return "KO"

#Fonction qui cherche les noms dans dans facebook a l'aide de l'API à partir d'un mot clef et insertion dans rapport.
def facebook_nom(n):
	
	long_token = get_extended_access_token(token, application_id, application_secret_key)
	
	response = requests.get('https://graph.facebook.com/search?q='+n+'&type=user&access_token='+(long_token[0])).text  
	data = json.loads(response)  
	try: 
		bogustext = 'Informations collectees sur Facebook au sujet de '+n+'.'
		p = Paragraph(bogustext, style)
		Story.append(p)
		Story.append(Spacer(1,0.2*inch))
		Story.append(Spacer(1,0.2*inch))
		for person in data['data']:  
					bogustext = "Nom: " + person['name']
					p = Paragraph(bogustext, style)
					Story.append(p)
					bogustext = "URL Facebook: http://www.facebook.com/" + person['id'] 
					p = Paragraph(bogustext, style)
					Story.append(p)
					Story.append(Spacer(1,0.2*inch))
		if "paging" in data:
					url = data["paging"]["next"]
					response = requests.get(url).text
					data = json.loads(response)
					for person in data['data']:  
						bogustext = "Nom: " + person['name']
						p = Paragraph(bogustext, style)
						Story.append(p)
						bogustext = "URL Facebook: http://www.facebook.com/" + person['id']
						p = Paragraph(bogustext, style)
						Story.append(p)
						Story.append(Spacer(1,0.2*inch))
		return "OK"
	except:
		return "KO"

#Fonction qui cherche les noms, groupes, évènements, et page dans dans facebook a l'aide de l'API à partir d'un mot clef et insertion dans rapport.
def facebook_all(n):

	bogustext = 'Informations collectees sur Facebook au sujet de '+n+'.'
	p = Paragraph(bogustext, style)
	Story.append(p)

	Story.append(Spacer(1,0.2*inch))
	Story.append(Spacer(1,0.2*inch))

	long_token = get_extended_access_token(token, application_id, application_secret_key)
	
	response = requests.get('https://graph.facebook.com/search?q='+n+'&type=user&access_token='+(long_token[0])).text  

	data = json.loads(response)   
	
	if "person" in data:
		for person in data['data']:  
				bogustext = "Nom: " + person['name']
				p = Paragraph(bogustext, style)
				Story.append(p)
				bogustext = "URL Facebook: http://www.facebook.com/" + person['id'] 
				p = Paragraph(bogustext, style)
				Story.append(p)
				Story.append(Spacer(1,0.2*inch))

	if "paging" in data:
            url = data["paging"]["next"]
	    response = requests.get(url).text  
	    data = json.loads(response)
	    for person in data['data']:  
				bogustext = "Nom: " + person['name']
				p = Paragraph(bogustext, style)
				Story.append(p)
	 	  		bogustext = "URL Facebook: http://www.facebook.com/" + person['id']
				p = Paragraph(bogustext, style)
				Story.append(p)
				Story.append(Spacer(1,0.2*inch))

	response = requests.get('https://graph.facebook.com/search?q='+n+'&type=group&access_token='+(long_token[0])).text 
	data = json.loads(response)   
	if "person" in data:
		for person in data['data']:  	
					bogustext = "Groupe: " + person['name'] 
					p = Paragraph(bogustext, style)
					Story.append(p)
					bogustext = "URL Facebook: http://www.facebook.com/" + person['id']
					p = Paragraph(bogustext, style)
					Story.append(p)
					Story.append(Spacer(1,0.2*inch)) 

	if "paging" in data:
            url = data["paging"]["next"]
	    response = requests.get(url).text  
	    data = json.loads(response)
	    for person in data['data']:  
		 		bogustext = "Groupe: " + person['name'] 
		 		p = Paragraph(bogustext, style)
				Story.append(p)
	 	  		bogustext = "URL Facebook: http://www.facebook.com/" + person['id']
				p = Paragraph(bogustext, style)
				Story.append(p)
				Story.append(Spacer(1,0.2*inch))

	response = requests.get('https://graph.facebook.com/search?q='+n+'&type=group&access_token='+(long_token[0])).text 
	data = json.loads(response)
	if "person" in data:   
		for person in data['data']:  
					bogustext = "Evenements: " + person['name'] 
					p = Paragraph(bogustext, style)
					Story.append(p)
					bogustext = "URL Facebook: http://www.facebook.com/" + person['id']
					p = Paragraph(bogustext, style)
					Story.append(p)
					Story.append(Spacer(1,0.2*inch)) 

	if "paging" in data:
            url = data["paging"]["next"]
	    response = requests.get(url).text  
	    data = json.loads(response)
	    for person in data['data']:  
				bogustext = "Evenements: " + person['name'] 
				p = Paragraph(bogustext, style)
				Story.append(p)
				bogustext = "URL Facebook: http://www.facebook.com/" + person['id']
				p = Paragraph(bogustext, style)
				Story.append(p)
				Story.append(Spacer(1,0.2*inch))

	response = requests.get('https://graph.facebook.com/search?q='+n+'&type=page&access_token='+(long_token[0])).text 
	data = json.loads(response)
	if "person" in data:   
		for person in data['data']:  
					bogustext = "Page: " + person['name'] 
					p = Paragraph(bogustext, style)
					Story.append(p)
					bogustext = "URL Facebook: http://www.facebook.com/" + person['id'] 
					p = Paragraph(bogustext, style)
					Story.append(p)
					Story.append(Spacer(1,0.2*inch))

	if "paging" in data:
            url = data["paging"]["next"]
	    response = requests.get(url).text  
	    data = json.loads(response)
	    for person in data['data']:  
				bogustext = "Page: " + person['name']
				p = Paragraph(bogustext, style)
				Story.append(p)
				bogustext = "URL Facebook: http://www.facebook.com/" + person['id']
				p = Paragraph(bogustext, style)
				Story.append(p)
				Story.append(Spacer(1,0.2*inch))

if __name__ == '__main__':
	G=nx.DiGraph()
	
	doc = SimpleDocTemplate("OSINT_"+keyword2+".pdf")
	Story = [Spacer(1,2*inch)]
	style = styles["Normal"]
    
	Story.append(Spacer(1,0.2*inch))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Spacer(1,0.2*inch))
	
	facebook_all(keyword2)
	linkedin_google_api(keyword2)

	driver = webdriver.Firefox()
	driver.get("http://www.linkedin.com")
	element = driver.find_element_by_id("session_key-login")
	element.send_keys(linke)
	element = driver.find_element_by_id("session_password-login")
	element.send_keys(passlinke)
	driver.find_element_by_id("btn-login").click()
	time.sleep(2)
	element = driver.find_element_by_id("main-search-box")
	element.send_keys(keyword2)
	driver.find_element_by_name("search").click()
	time.sleep(2)
	x = 0
	y = 0	
	while check_exists("paginator-next"):
	#while y < 2:
		#y += 1
		list_links = driver.find_elements_by_tag_name('img')
		#x = 0	
		time.sleep(1)
		for i in list_links:
			time.sleep(2)
			try:
				image_liens = i.get_attribute('src')
				pattern = "[^ ].*?\.(jpg)"
				if re.search(pattern, image_liens):

					download(image_liens,(str(x))+".jpg")

					time.sleep(1)
					Story.append(Spacer(1,0.2*inch))
					path_image = repertoire_tmp+(str(x))+".jpg"
					nom = google_reverse(path_image)
					#im = Image(path_image, 2*inch, 2*inch)
					#Story.append(im)
					#Story.append(Spacer(1,0.2*inch))
					x += 1
					if nom != '':
						nom_url = nom.encode('utf8')
						print nom_url
						google(nom_url)   
						if linkedin_nom(nom_url) == 'OK': 
						
							if facebook_nom(nom_url) == "KO":
								break
							else:
								print "token OK"
						else:
							print "erreur linkedin"
			except:
				x += 1
				break
				
						
									
		driver.find_element_by_class_name("paginator-next").click()
		time.sleep(2)
		
	driver.close()
	
	plt.figure(figsize=(30,30))
	nx.draw(G)
	# Set your output filename
	plt.savefig(keyword2+'.png')
	
	img2 = keyword2+'.png'
	bogustext = "Graphique des profils linkedin découverts: "
	p = Paragraph(bogustext, style)
	Story.append(p)
	Story.append(Spacer(1,0.2*inch))
	im = Image(img2, 7*inch, 7*inch)
	Story.append(im)
	#fichier = 'OSINT_'+.html'
	doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

