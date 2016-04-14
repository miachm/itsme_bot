#!/usr/bin/python
# -*- coding: utf-8 -*-

import telebot 
from telebot import types

import ConfigParser
import traceback
import time
import re
import random
import sqlite3
from datetime import datetime
import threading
import schedule

# Imports propios
from bot_graphs import graph_statsFrom, graph_statsFrom2
from bot_stats import statsFrom, statsFrom2
import bot_eolparser

#########################################################################
# Globales
#########################################################################
	
# Parseador para el fichero bot.cfg
cfg_parser = ConfigParser.ConfigParser()

try:
	cfg_parser.read('bot.cfg')
except:
	print "No se puede leer bot.cfg"
	quit()
	
try:
	TOKEN         = cfg_parser.get('settings', 'token')     # Bot token
	expruebas_cid = cfg_parser.getint('settings', 'cid_group') # id del chat de grupo
	my_cid        = cfg_parser.getint('settings', 'cid_user')  # id del chat individual
	
	print TOKEN
	print expruebas_cid
	print my_cid
except:
	print "Configuración incorrecta en bot.cfg"
	traceback.print_exc()
	quit()

bot    = telebot.TeleBot(TOKEN) 
oldTh  = bot_eolparser.loadThreads('forito.bin') 

admins        = ["Korso10"]
warn_noadmin  = "Va a ser que no, parguela."


# fantas
fanteables = ['Reifeen', 'Miriamele', 'shenita91','Lazzeru']
fantas     = ['¿Unas fantas, juapa?', '¡Fotoescote ya!', '¿Unas sidras, hermosa?']
fantasprob = 0.2

# antispam
spamcount  = 0
spamlimit  = 5
spammers   = ['Erikoptero']
spamreply  = ['Te pires', 'Pesao', 'Y sigue...', 'Paso de ti', 'Qué cansino joder']
banreply   = ['¿No te cansas, parguela? Te ignoro un rato.']
	
	
	
########################################################################
# Tratamiento de unicode: decode early, encode lazy
# http://farmdev.com/talks/unicode/
########################################################################

def toUnicode(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj



########################################################################
# Funciones periodicas
########################################################################

def bcast_stats():
	bot.send_message(expruebas_cid,"Nuevo día. Veamos las estadísticas:")
	statsFrom2(bot,expruebas_cid,3600*24,"Flood en el último dia",True)
	graph_statsFrom2(bot,expruebas_cid,3600*24,"Flood en el ultimo dia", True)
	
def bcast_stats_h():
	statsFrom2(bot,expruebas_cid,3600,"Flood en la última hora",True)
	graph_statsFrom2(bot,expruebas_cid,3600,"Flood en la ultima hora", True)
	
def check_forum(cid):
	global oldTh
	
	# Mostramos nuevos hilos del foro
	newTh = bot_eolparser.get_new_threads(oldTh)
	
	if len(newTh) == 0:
		bot.send_message(cid, "Nada nuevo en el forito")
	else:
		for th in newTh:
			msg =  "<b>Nuevo hilo de %s</b>:\n" % th[3]
			msg += '<a href="%s">%s</a>' % (th[2],th[1])
			print msg
			bot.send_message(cid, msg, parse_mode="HTML")
	
	# Actualizamos oldTh para que no vuelva a repetir hilos
	oldTh = bot_eolparser.get_threads()
	# Guardamos hilos actualizados en el archivo por si peta el bot
	bot_eolparser.saveThreads('forito.bin',oldTh)

def bcast(cid):
	bot.send_message(cid, "Probando...")

def daily_worker(interval=1):
	while True:
		schedule.run_pending()
		time.sleep(interval)	
	

		
########################################################################
# Log de mensajes y relacionados
########################################################################	
		
# Esta funcion añade cada mensaje a la db para el conteo diario
def msg_handler(m):
	user = m.from_user.username
	text = m.text
	mid = m.message_id
	time = m.date
	chatid = m.chat.id
	
	print "[id: %s][%s][%s]: %s" % (mid, time, user, text)
		
	# Metemos el mensaje en la db temporal 
	try:
		newmsg = "INSERT INTO messagelog VALUES('%s', '%s', '%s', '%s', '%s')" % (mid, user, time, text, chatid)
		con = sqlite3.connect('telegram.db')
		cur = con.cursor()
		
		cur.execute(newmsg)
		con.commit()
		con.close()
	except:
		print "Error añadiendo mensaje a db -> messagelog"
		traceback.print_exc()
	print "Nuevo mensaje añadido a db"
		

# Esta funcion borra la db de mensajes, reiniciando el conteo
def del_messagelog(m):
	try:
		del_table = "DELETE FROM messagelog;"
		con = sqlite3.connect('telegram.db')
		cur = con.cursor()
		
		cur.execute(del_table)
		con.commit()
		con.close()
		print "Tabla messagelog borrada"
	except:
		print "Error borrando tabla messagelog"
		traceback.print_exc()


# Esta funcion actualiza el ultimo mensaje de cada usuario junto con su fecha
# la tabla donde se guardan estos datos es diferente a la que usa la funcion 
# msg_handler
def update_msg(m, debug = False):
	try:
		user = m.from_user.username
		msgtext = m.text
		date = m.date
	except:
		print "Error parseando mensaje (update_msg)"
	
	try:
		checkuser   = "SELECT user,msgcount FROM lastmessage WHERE user = '"+user+"';"
		update1_cmd = "UPDATE lastmessage SET msg = '"+msgtext+"' WHERE user = '"+user+"';"
		update2_cmd = "UPDATE lastmessage SET time = '"+str(date)+"' WHERE user = '"+user+"';"
		newuser_cmd = "INSERT INTO lastmessage VALUES('"+user+"',"+str(date)+",'"+msgtext+"',0)"
	   
		con = sqlite3.connect('telegram.db')
		cur = con.cursor()
		
		# Verificamos si existe el usuario
		cur.execute(checkuser)
		data=cur.fetchone()
		
		# Si no existe, lo agregamos a la tabla
		if data is None:
			print "Agregando a",user,"a la db"
			cur.execute(newuser_cmd)
		# Si existe, actualizamos el ultimo mensaje
		else:
			print "Actualizando mensaje de",user
			cur.execute(update1_cmd)
			cur.execute(update2_cmd)
			cur.execute("UPDATE lastmessage SET msgcount = "+str(int(data[1])+1)+" WHERE user ='"+user+"';")
		con.commit()
		con.close()
	except:
		print "Error añadiendo mensaje a db"
		print "checkuser:",checkuser
		print "update:", update1_cmd, update2_cmd
		print "new:", newuser_cmd
		traceback.print_exc()
		

# Esta funcion consulta la db y envia un mensaje con las estadisticas
def showmsgcount(m, debug = False):
	cid = m.chat.id
	query = "select user, msgcount from lastmessage order by msgcount desc;"
	
	try:
		con = sqlite3.connect('telegram.db')
		cur = con.cursor()
		
		# Ejecutamos consulta y recogemos lista de mensajes
		cur.execute(query)
		rows = cur.fetchall()
		
		response = u""
		for row in rows:
			print row[0], row[1]
			response += str("<b>"+row[0]+"</b>: "+str(row[1])+"\n")
		
		bot.send_message(cid, response, parse_mode="HTML")
	except:
		print "Error in showmsgcount"
		traceback.print_exc()
		
# Esta funcion envia un mensaje indicando cuando un usuario envio su ultimo
# mensaje y que dijo
def lastwords(user):
	try:
		checkwords = "SELECT msg, time FROM lastmessage WHERE user = '"+user+"';"
		
		con = sqlite3.connect('telegram.db')
		cur = con.cursor()
		
		# Verificamos si existe el usuario
		cur.execute(checkwords)
		data=cur.fetchone()
		
		# Si no existe, lo agregamos a la tabla
		if data is None:
			return "Ni idea"
		# Si existe, actualizamos el ultimo mensaje
		else:
			timestamp = time.strftime("%d/%b - %H:%M",time.localtime(int(data[1])+6*3600))
			return "<b>["+timestamp+"]:</b> "+data[0]
		con.close()
	except:
		print "Error añadiendo mensaje a db"
		traceback.print_exc()




########################################################################
# Funciones del bot
########################################################################

# Funcion para responder al /me
@bot.message_handler(commands=["me"]) 
def command_me(m):
	global spamcount
	global spamlimit
	
	try:
		cid = m.chat.id
		username = m.from_user.first_name
		usernick = m.from_user.username
		msgtext = ""

		msg_unparsed = re.match(r'/me (.+)',m.text)
		if msg_unparsed:
			msgtext = msg_unparsed.group(1)
			
		if usernick in fanteables and fantasprob < random.random():
			reply = random.choice(fantas)
		else: 
			reply = "<i>" + unicode(username) + " " + unicode(msgtext) + "</i>"
		
		if usernick not in spammers:
			bot.send_message(cid, reply, parse_mode="HTML")
		else:
			if spamcount > spamlimit:
				pass
			elif spamcount == spamlimit:
				spamcount = spamcount + 1
				bot.send_message(cid, random.choice(banreply))
			else:
				spamcount = spamcount + 1
				bot.send_message(cid, random.choice(spamreply))
	except:
		traceback.print_exc()


		
# Funcion para obtener el ultimo mensaje de un user
@bot.message_handler(commands=["lastwords"]) 
def command_lastwords(m):
	try:
		cid = m.chat.id
		print m.text
		lastwords_user = re.match(r'/lastwords(\@[Ii]tsme_[Kk]_bot)?.+\@(\w+).*',m.text)
		if lastwords_user:
			reply = lastwords(lastwords_user.group(2))
		else:
			reply = "Escribe /lastwords @usuario para buscar lo último que dijo @usuario"
			
		bot.send_message(cid, reply, parse_mode="HTML")
	except:
		traceback.print_exc()
		
		
# Funcion para listar mensajes
@bot.message_handler(commands=["flooders"])
def command_flooders(m):
	showmsgcount(m)
		

# Funcion de estadisticas de la ultima hora
@bot.message_handler(commands=["stats1h"])
def stats1h(m):
	statsFrom(bot,m,3600, "Flood en la ultima hora", True)
	graph_statsFrom(bot,m,3600,"Flood en la ultima hora", True)
		
	
# Funcion de estadisticas del ultimo dia
@bot.message_handler(commands=["stats1d"])
def stats1d(m):
	statsFrom(bot,m,3600*24, "Flood en el ultimo dia", True)
	graph_statsFrom(bot,m,3600*24,"Flood en el ultimo dia", True)
	
# Funcion de estadisticas de la ultima semana
@bot.message_handler(commands=["stats1s"])
def stats1s(m):
	statsFrom(bot,m,3600*24*7, "Flood en la ultima semana", True)
	graph_statsFrom(bot,m,3600*24*7,"Flood en la ultima semana", True)
	
	
# Funcion de estadisticas de la ultima hora
@bot.message_handler(commands=["allstats1h"])
def allstats1h(m):
	usernick = m.from_user.username
	if usernick in admins:
		statsFrom(bot,m,3600, "Flood en la ultima hora", False)
		graph_statsFrom(bot,m,3600,"Flood en la ultima hora", False)
	else:
		bot.send_message(cid, warn_noadmin)
		
# Funcion de estadisticas del ultimo dia
@bot.message_handler(commands=["allstats1d"])
def allstats1d(m):
	usernick = m.from_user.username
	if usernick in admins:
		statsFrom(bot,m,3600*24, "Flood en el ultimo dia", False)
		graph_statsFrom(bot,m,3600*24,"Flood en el ultimo dia", False)
	else:
		bot.send_message(cid, warn_noadmin)
			
# Funcion de estadisticas de la ultima semana
@bot.message_handler(commands=["allstats1s"])
def allstats1s(m):
	usernick = m.from_user.username
	if usernick in admins:
		statsFrom(bot,m,3600*24*7, "Flood en la ultima semana", False)
		graph_statsFrom(bot,m,3600*24*7,"Flood en la ultima semana", False)
	else:
		bot.send_message(cid, warn_noadmin)
	
# Funcion para buscar nuevos hilos en ex-pruebas
@bot.message_handler(commands=["pruebas"])
def newinpruebas(m):
	global oldTh
	cid = m.chat.id
	
	usernick = m.from_user.username
	if usernick in admins:
		newTh = bot_eolparser.get_new_threads(oldTh)
		
		if newTh == None:
			bot.send_message(cid, "No puedo leer el forito. Culpa de melado.")
			return
		if len(newTh) == 0:
			bot.send_message(cid, "Nada nuevo en el forito")
		for th in newTh:
			msg =  "<b>Nuevo hilo de %s</b>:\n" % th[3]
			msg += '<a href="%s">%s</a>' % (th[2],th[1])
			print msg
			bot.send_message(cid, msg, parse_mode="HTML")
	else:
		bot.send_message(cid, warn_noadmin)
		
		
		
# Funcion general. 
@bot.message_handler(func=lambda m: True)
def process_all(m):
	
	try:
		cid = m.chat.id
		username = m.from_user.first_name
		usernick = m.from_user.username
		msgtext = toUnicode(m.text)

		# log
		logmsg = "["+str(time.asctime())+"]"+"["+str(cid)+"] - ["+unicode(usernick)+"]: "+msgtext
		print logmsg.encode('utf-8')

		# Añadimos el mensaje a la db
		update_msg(m)
		msg_handler(m)
		
	except:
		traceback.print_exc()


# Funcion para borrar tabla messagelog
@bot.message_handler(commands=["delmsglog"]) 
def delmsglog(m):
	cid = m.chat.id
	username = m.from_user.first_name
	usernick = m.from_user.username
	response = ""
	
	if usernick in admins:
		del_messagelog()
		bot.send_message(cid, "Tabla messagelog borrada")
	else:
		bot.send_message(cid, warn_noadmin)



def main():
	

	# db para ultimo mensaje
	try:
		con = sqlite3.connect('telegram.db')
		cur = con.cursor()
	except:
		print 'Error abriendo telegram.db'
		if con:
			con.close()

	# Lanzando hilos de scheduling
	schedule.every().day.at("00:00").do(bcast_stats)
	
	# Lanzando resumenes de cada hora para que sea siempre a en punto
	schedule.every().day.at("01:00").do(bcast_stats_h)
	schedule.every().day.at("02:00").do(bcast_stats_h)
	schedule.every().day.at("03:00").do(bcast_stats_h)
	schedule.every().day.at("04:00").do(bcast_stats_h)
	schedule.every().day.at("05:00").do(bcast_stats_h)
	schedule.every().day.at("06:00").do(bcast_stats_h)
	schedule.every().day.at("07:00").do(bcast_stats_h)
	schedule.every().day.at("08:00").do(bcast_stats_h)
	schedule.every().day.at("09:00").do(bcast_stats_h)
	schedule.every().day.at("10:00").do(bcast_stats_h)
	schedule.every().day.at("11:00").do(bcast_stats_h)
	schedule.every().day.at("12:00").do(bcast_stats_h)
	schedule.every().day.at("13:00").do(bcast_stats_h)
	schedule.every().day.at("14:00").do(bcast_stats_h)
	schedule.every().day.at("15:00").do(bcast_stats_h)
	schedule.every().day.at("16:00").do(bcast_stats_h)
	schedule.every().day.at("17:00").do(bcast_stats_h)
	schedule.every().day.at("18:00").do(bcast_stats_h)
	schedule.every().day.at("19:00").do(bcast_stats_h)
	schedule.every().day.at("20:00").do(bcast_stats_h)
	schedule.every().day.at("21:00").do(bcast_stats_h)
	schedule.every().day.at("22:00").do(bcast_stats_h)
	schedule.every().day.at("23:00").do(bcast_stats_h)
	
	# Este falla de momento
	#schedule.every().hour.do(check_forum,expruebas_cid)
	
	# Lanza el daily_worker, que va comprobando los schedules
	t = threading.Thread(target=daily_worker)
	t.start()

	# Obviar fallos de la API de Telegram
	bot.polling(none_stop=True)



# Codigo de entrada
if __name__ == "__main__":
	main()
