#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import html
from bs4 import BeautifulSoup
import requests
import hashlib
import pickle
import traceback


print "Loaded eolparser.py"

headers = {'user-agent': 'Korso10 Bots'}

urlforito = 'http://www.elotrolado.net/foro_off-topic-ex-pruebas_21'
urlbase = 'http://www.elotrolado.net'

# Tratamiento de unicode: decode early, encode lazy
def toUnicode(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj

def get_threads():
	page = requests.get(urlforito, headers=headers)
	print "[requests.get]",page.status_code
	tree = html.fromstring(page.content)
	soup = BeautifulSoup(page.content)

	forum_thread = []

	# Extraemos los titulos de los hilos con su enlace, y calculamos un hash
	# basandonos en dicho enlace
	for row in soup.find_all("div",class_="col-xs-24 title"):
		try:
			new_title = row.a['title']                    # Titulo del hilo
			new_link = urlbase+'/'+row.a['href']          # Link del hilo
			new_hash = hashlib.sha1(new_link).hexdigest() # Hash rapido para comprobar duplicados
			
			# Añadimos a forum thread
			forum_thread.append([toUnicode(new_hash), toUnicode(new_title), toUnicode(new_link)])
		except KeyError:
			print "Nada"

	# Eliminamos el primer hilo, que es el de las normas de foro y no nos sirve
	try:
		del(forum_thread[0])
	except:
		print "No se puede borrar el primer hilo del foro ¿Fallo en el get?"	
		traceback.print_exc()
		return None
		
	# Extraemos autores de cada hilo y los unimos al array
	for idx,link in enumerate(soup.find_all("div",class_="col-xs-24 col-sm-12 author")):
		try:
			new_author = link.a.get_text()
			forum_thread[idx].append(toUnicode(new_author))
		except KeyError:
			print "Nada"
		
	# Devolvemos los hilos de la primera pagina (hash, title, link, author)
	return forum_thread
	
	
def get_new_threads(old_threads_list):
	possible_threads_list = get_threads()
	
	if possible_threads_list == None:
		print "No se puede actualizar los nuevos hilos. ¿Fallo en el get?"
		return
		
	new_threads = []
	
	for newth in possible_threads_list:
		new = True
		
		for oldth in old_threads_list:
			#~ print "Comparando %s con %s" 
			if newth[0] == oldth[0]:
				new = False
				
		if new:
			new_threads.append(newth)
	
	return new_threads

def print_threads(threadlist):
	for th in threadlist:
		print "Hash:  ",th[0], type(th[0])
		print "Titulo:",th[1], type(th[1])
		print "Link:  ",th[2], type(th[2])
		print "Autor: ",th[3], type(th[3])
		print "----------------------------------------------------------"
	print "Total hilos:",len(threadlist)
	
	
def saveThreads(filename, threadlist):
	try:
		outFile = open(filename, 'wb')
		pickle.dump(threadlist,outFile)
		outFile.close()
		print "%s guardado correctamente." % filename
	except:
		print "Error guardando hilos en %s" % filename	
		traceback.print_exc()
	
def loadThreads(filename):
	auxTh = []
	try:
		inFile = open(filename,'rb')
		auxTh = pickle.load(inFile)
	except:
		print "Error cargando hilos de %s" % filename	
		traceback.print_exc()
	return auxTh


