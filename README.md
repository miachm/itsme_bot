# itsme_bot

Bot para el grupo de ex-pruebas en Telegram.

# Instalación

`itsme_bot` utiliza la librería [telebot](https://github.com/eternnoir/pyTelegramBotAPI) 
para interactuar con Telegram. Se puede instalar con `pip`.

Antes de ejecutar el código es necesario crear el bot primero para obtener un token. 
Para ello se usa el bot `@Botfather` disponible en Telegram. Hay un tutorial disponible para
hacer esto [aquí](http://www.forocoches.com/foro/showthread.php?t=4491359).

Una vez obtenido el token, se debe crear un fichero `bot.cfg` siguiendo el siguiente
formato:

    [settings]
    token     = <token del bot>
    cid_group = <id del grupo donde va a estar el bot>
    cid_user  = <id del administrador del bot>

Una vez guardado el fichero `bot.cfg`, se puede ejecutar `bot.py` para arrancar el bot.

# Base de datos telegram.db

`itsme_bot` utiliza una base de datos sqlite3 para almacenar la información necesaria
para generar estadísticas. La base de datos se encuentra en el fichero `telegram.db`
y contiene dos tablas:

## Tabla lastmessage

Se utiliza para que el comando `/lastwords @usuario` devuelva el último mensaje
del usuario. Tiene como clave el user de Telegram, y como resto de campos el 
timestamp (en formato UNIX), el contenido del último mensaje y un contador de mensajes.

La tabla se puede replicar con:

	CREATE TABLE lastmessage(
	user char(50) primary key not null,
	time char(50) not null,
	msg text
	serialized blob, msgcount integer);

## Tabla messagelog

Se utiliza para generar las gráficas de mensajes. La clave primaria es el id de
mensaje que devuelve Telegram, que es único para cada mensaje. El resto de campos
son el usuario el tiempo y el mensaje, similares a la tabla lastmessage, y el id
del chat, para que sólo muestre las estadísticas del grupo que las haya solicitado.

La tabla se puede replicar con:

	CREATE TABLE messagelog (
    "mid" INTEGER NOT NULL,
    "user" TEXT NOT NULL,
    "time" INTEGER NOT NULL,
    "msg" TEXT NOT NULL,
    "chatid" TEXT NOT NULL DEFAULT (0));
    
telegram_blank.db contiene las tablas anteriores creadas y vacías. Es necesario
renombrar este fichero a telegram.db antes de usar el bot.


	

