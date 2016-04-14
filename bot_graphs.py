#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import matplotlib.font_manager as font_manager
import time
import traceback


path = './fonts/xkcd-Regular.ttf'
prop = font_manager.FontProperties(fname=path)
lastgraph = 0

print "Loaded bot_graphs.py"


def graph_statsFrom(bot,m,secondsFrom=3600,graphTitle="Flood",onlyThisChat=True):
	cid = m.chat.id
	username = m.from_user.first_name
	usernick = m.from_user.username
	curtime = m.date
	global lastgraph

	# Para que no abusen
	if lastgraph > curtime:
		bot.send_message(cid, "No tan rápido, parguela.")
		return
	else:
		lastgraph = curtime + 30
		
	from_time = curtime - secondsFrom

	# Vamos a consultar la tabla para extraer los datos de hace una hora 
	try:
		queryThisChat = "SELECT user, count(msg) FROM messagelog WHERE time >= %d AND chatid = %d GROUP BY user ORDER BY count(msg) desc" % (from_time, cid)
		queryAllChats = "SELECT user, count(msg) FROM messagelog WHERE time >= %d GROUP BY user ORDER BY count(msg) desc" % (from_time)
		con = sqlite3.connect('telegram.db')
		cur = con.cursor()
		
		if onlyThisChat:
			cur.execute(queryThisChat)
		else:
			cur.execute(queryAllChats)
		rows = cur.fetchall()
		
		xlabels = []
		ycount = []
		
		for row in rows:
			xlabels.append(row[0][:10])
			ycount.append(int(row[1]))
		con.close()
	except:
		print "Error en graph_statsFrom"
		traceback.print_exc()


	# Dibujamos grafica
	N = len(xlabels)
	nb_messages = ycount
	
	# posicion de las barras
	ind = np.arange(N)
	
	# Width of the bars
	width = 0.35
	
	# Dibujamos grafica
	plt.xkcd()
	fig = plt.figure()
	ax = fig.add_subplot(111)
	rects = ax.bar(ind+width*0.5, nb_messages, width, color = 'r')
	
	# Add cosillas
	ax.set_ylabel('Mensajes', fontproperties=prop, size=18)
	ax.set_title(graphTitle,fontproperties=prop, size=24)
	ax.set_xticks(ind+width)
	plt.xticks(rotation=90)
	ax.set_xticklabels(xlabels, fontproperties=prop, size=18)
	for label in ax.get_yticklabels() :
		label.set_fontproperties(prop)
		label.set_size(18)

	# Ajustamos margen
	plt.tight_layout()
	
	# Mostramos
	plt.savefig("graph.png")
	
	# Enviamos imagen al chat
	bot.send_chat_action(cid, 'upload_photo')
	img = open('graph.png', 'rb')
	bot.send_photo(m.chat.id, img)
	img.close()


def graph_statsFrom2(bot,cid,secondsFrom=3600,graphTitle="Flood",onlyThisChat=True):
	curtime = int(time.time())
	global lastgraph

	# Para que no abusen
	if lastgraph > curtime:
		bot.send_message(cid, "No tan rápido, parguela.")
		return
	else:
		lastgraph = curtime + 30
		
	from_time = curtime - secondsFrom

	# Vamos a consultar la tabla para extraer los datos de hace una hora 
	try:
		queryThisChat = "SELECT user, count(msg) FROM messagelog WHERE time >= %d AND chatid = %d GROUP BY user ORDER BY count(msg) desc" % (from_time, cid)
		queryAllChats = "SELECT user, count(msg) FROM messagelog WHERE time >= %d GROUP BY user ORDER BY count(msg) desc" % (from_time)
		con = sqlite3.connect('telegram.db')
		cur = con.cursor()
		
		if onlyThisChat:
			cur.execute(queryThisChat)
		else:
			cur.execute(queryAllChats)
		rows = cur.fetchall()
		
		xlabels = []
		ycount = []
		
		for row in rows:
			xlabels.append(row[0][:10])
			ycount.append(int(row[1]))
		con.close()
	except:
		print "Error en graph_statsFrom"
		traceback.print_exc()


	# Dibujamos grafica
	N = len(xlabels)
	nb_messages = ycount
	
	# posicion de las barras
	ind = np.arange(N)
	
	# Width of the bars
	width = 0.35
	
	# Dibujamos grafica
	plt.xkcd()
	fig = plt.figure()
	ax = fig.add_subplot(111)
	rects = ax.bar(ind+width*0.5, nb_messages, width, color = 'r')
	
	# Add cosillas
	ax.set_ylabel('Mensajes', fontproperties=prop, size=18)
	ax.set_title(graphTitle,fontproperties=prop, size=24)
	ax.set_xticks(ind+width)
	plt.xticks(rotation=90)
	ax.set_xticklabels(xlabels, fontproperties=prop, size=18)
	for label in ax.get_yticklabels() :
		label.set_fontproperties(prop)
		label.set_size(18)

	# Ajustamos margen
	plt.tight_layout()
	
	# Mostramos
	plt.savefig("graph.png")
	
	# Enviamos imagen al chat
	bot.send_chat_action(cid, 'upload_photo')
	img = open('graph.png', 'rb')
	bot.send_photo(cid, img)
	img.close()
