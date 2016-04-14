#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import time
import traceback 

print "Loaded bot_stats.py"

def statsFrom(bot,m,secondsFrom=3600,statsTitle="Flood en la ultima hora",onlyThisChat=True,showTotal=True):
	cid = m.chat.id
	username = m.from_user.first_name
	usernick = m.from_user.username
	curtime = m.date
	response = ""
	from_time = curtime - secondsFrom
	total = 0
	
	# Escribimos titulo
	response += statsTitle
	response += "\n"
	
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
		
		for row in rows:
			response += str("<b>"+row[0]+"</b>: "+str(row[1])+"\n")
			total += int(row[1])
		con.close()
		if showTotal:
			response += str("\n<b>Total:</b> "+str(total)+" mensajes")
		bot.send_message(cid, response, parse_mode="HTML")
	except:
		print "Error en graph_statsFrom"
		traceback.print_exc()
	
	
def statsFrom2(bot,cid,secondsFrom=3600,statsTitle="Flood en la ultima hora",onlyThisChat=True,showTotal=True):
	curtime = int(time.time())
	response = ""
	from_time = curtime - secondsFrom
	total = 0
	
	# Escribimos titulo
	response += statsTitle
	response += "\n"
	
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
		
		for row in rows:
			response += str("<b>"+row[0]+"</b>: "+str(row[1])+"\n")
			total += int(row[1])
		con.close()
		if showTotal:
			response += str("\n<b>Total:</b> "+str(total)+" mensajes")
		bot.send_message(cid, response, parse_mode="HTML")
	except:
		print "Error en graph_statsFrom2"
		traceback.print_exc()
