#!/bin/python3
import configparser
import random
from random import randint
from time import time

import psycopg2

config = configparser.ConfigParser()
config.read('config.ini')

con = psycopg2.connect(config.get('database', 'dsn'))
cur = con.cursor()


# Returns a string format of current time
# in discord's relative time format eg <t:2343534353:R>
def get_time_date():
  now = f"<t:{str(time())[:10]}:R>"
  return now


# Retruns a string format of delayed time
# in discord's relative time format eg <t:2343534353:R>
def get_delayed_time(delay):
  delayed_time = f"<t:{str(float(time()) - delay)[:10]}:R>"
  return delayed_time


with con:
  cur.execute("""CREATE TABLE IF NOT EXISTS Config
        (NAME text, guildid bigint, VALUE text)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS SlaveDB
        (slaveid bigint, guildid bigint, gag text, tiechannel bigint, emoji boolean, lines INTEGER, chastity boolean, muff boolean, life INT)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS Ownership
        (slaveid bigint, guildid bigint, ownerid bigint, rank INTEGER, str_time text)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS Badwords
        (slaveid bigint, dommeid bigint, guildid bigint, word text, str_time text)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS Prison
        (slaveid bigint, guildid bigint, dommeid bigint, num INTEGER, sentence text, COUNT INTEGER, roles text)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS Blacklist
        (memberid bigint, guildid bigint)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS Money
        (memberid bigint, guildid bigint, coin bigint, gem bigint)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS Worship
        (memberid bigint, guildid bigint, simp text)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS ESCAPE
        (memberid bigint, guildid bigint, timeint bigint, TYPE text)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS Botban
        (memberid bigint, timeint bigint, reason text)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS ChessData
        (memberid bigint, guildid bigint, wincount INT, losecount INT, drawcount INT, point INT, playingwith bigint)""")

  cur.execute("""CREATE TABLE IF NOT EXISTS ChessMatch
        (player bigint, guildid bigint, game bytea, endtime bigint)""")


##############################################################################
#                                                                            #
#                                                                            #
#                                  CONFIG                                    #
#                                                                            #
#                                                                            #
##############################################################################

def insert_config(name, guild, value):
  with con:
    cur.execute("DELETE FROM Config WHERE name = %s AND guildid = %s", (name, int(guild)))
    cur.execute("INSERT INTO Config (name, guildid, value) VALUES (%s, %s, %s)", (name, int(guild), str(value)))


def append_config(name, guild, value):
  with con:
    cur.execute("UPDATE Config SET value = value || %s WHERE name = %s AND guildid = %s",
                (str(value), name, int(guild)))


def clear_config(name, guild):
  with con:
    cur.execute("DELETE FROM Config WHERE name = %s AND guildid = %s", (name, int(guild)))


def get_config(name, guild):
  cur.execute("SELECT value FROM Config WHERE name =%s AND guildid = %s", (name, int(guild)))
  value = []

  try:
    data = cur.fetchall()[0][0]
    return data.split(',')
  except IndexError:
    return [0]



def get_config_raw(name, guild):
  try:
    cur.execute("SELECT value FROM Config WHERE name =%s AND guildid =%s", (name, guild))
    raw_value = cur.fetchall()[0][0]
    return raw_value
  except IndexError:
    return


def is_config(guild):
  if [0] == get_config('domme', guild):
    return False
  if [0] == get_config('slave', guild):
    return False
  if [0] == get_config('locker', guild):
    return False
  if [0] == get_config('prisoner', guild):
    return False
  if [0] == get_config('prison', guild):
    return False
  return True


def remove_guild(guild):
  with con:
    cur.execute("DELETE FROM Config WHERE guildid = %s", (guild,))
    cur.execute("DELETE FROM SlaveDB WHERE guildid = %s", (guild,))
    cur.execute("DELETE FROM Ownership WHERE guildid = %s", (guild,))
    cur.execute("DELETE FROM Badwords WHERE guildid = %s", (guild,))
    cur.execute("DELETE FROM Prison WHERE guildid = %s", (guild,))
    cur.execute("DELETE FROM Money WHERE guildid = %s", (guild,))
    cur.execute("DELETE FROM Worship WHERE guildid = %s", (guild,))

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                 WORSHIP                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################


def simp(member, guild, women):
  cur.execute("SELECT * FROM Worship WHERE memberid = %s AND guildid = %s", (member, guild))
  data = cur.fetchall()
  if data == []:
    with con:
      cur.execute("INSERT INTO Worship (memberid, guildid, simp) VALUES (%s, %s, %s)",
                  (member, guild, str(women) + '_1'))
  else:
    data = data[0][2]
    if str(women) in data:
      temp = []
      data = data.split('/')
      for d in data:
        x = d.split('_')
        if x[0] == str(women):
          x[1] = str(int(x[1]) + 1)
        x = '_'.join(x)
        temp.append(x)
      data = '/'.join(temp)
      with con:
        cur.execute("UPDATE Worship SET simp = %s WHERE memberid = %s AND guildid = %s", (data, member, guild))
    else:
      with con:
        cur.execute("UPDATE Worship SET simp = simp || %s WHERE memberid = %s AND guildid = %s",
                    ('/' + str(women) + '_1', member, int(guild)))


def get_simp(member, guild):
  cur.execute("SELECT simp FROM Worship WHERE memberid =%s AND guildid =%s", (member, guild))
  try:
    temp = []
    total_simp = 0
    data = cur.fetchall()[0][0].split('/')
    for d in data:
      x = d.split('_')
      x = [int(x[0]), int(x[1])]
      total_simp += x[1]
      temp.append(x)
    return [temp, total_simp]
  except IndexError:
    return

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                  FEMDOM                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################


def insert_slave_to_DB(member, guild):
  with con:
    cur.execute(
      "INSERT INTO SlaveDB (slaveid, guildid, gag, tiechannel, emoji, lines, chastity, muff, life) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
      (member, guild, 'off', 0, True, 0, True, True, 10))
  return [(member, guild, 'off', 0, True, 0, True, True, 10)]


def remove_member(member, guild):
  with con:
    cur.execute("DELETE FROM SlaveDB WHERE slaveid=%s AND guildid = %s", (member, guild))
    cur.execute("DELETE FROM Ownership WHERE slaveid=%s AND guildid = %s", (member, guild))
    cur.execute("DELETE FROM Ownership WHERE ownerid=%s AND guildid = %s", (member, guild))
    cur.execute("DELETE FROM Badwords WHERE slaveid=%s AND guildid = %s", (member, guild))
    cur.execute("DELETE FROM Badwords WHERE dommeid=%s AND guildid = %s", (member, guild))
    cur.execute("DELETE FROM Prison WHERE slaveid=%s AND guildid = %s", (member, guild))
    cur.execute("DELETE FROM Money WHERE memberid=%s AND guildid = %s", (member, guild))
    cur.execute("DELETE FROM Worship WHERE memberid=%s AND guildid = %s", (member, guild))


def get_slave_from_DB(member, guild):
  cur.execute("SELECT * FROM SlaveDB WHERE slaveid = %s AND guildid = %s", (member, guild))
  slave_data = cur.fetchall()
  if not slave_data:
    return insert_slave_to_DB(member, guild)
  else:
    return slave_data


def get_owner(member, guild):
  cur.execute("""SELECT ownerid FROM Ownership WHERE slaveid = %s AND guildid = %s""", (member, guild))
  ownerid = cur.fetchall()
  try:
    return ownerid[0][0]
  except IndexError:
    return 0


def own_a_slave(owner, slave, guild):
  with con:
    cur.execute(
      "INSERT INTO Ownership (slaveid, guildid, ownerid, rank, str_time) VALUES (%(slaveid)s, %(guildid)s, %(ownerid)s, %(rank)s, %(str_time)s)",
      {'slaveid': slave,
       'guildid': guild,
       'ownerid': owner,
       'rank': 1000,
       'str_time': get_time_date()})


def disown_a_slave(member, guild):
  with con:
    cur.execute("DELETE FROM Ownership WHERE slaveid = %s AND guildid = %s", (member, guild))
    cur.execute("DELETE FROM Badwords WHERE slaveid = %s AND guildid = %s", (member, guild))
    cur.execute(
      "UPDATE SlaveDB SET gag=%s, tiechannel=%s, emoji=%s, chastity=%s, muff=%s WHERE slaveid=%s AND guildid = %s",
      ['off', 0, True, True, True, member, guild])


def update_slaveDB(member, column, value, guild):
  print(f'updating slave, {column=} will now be {value=}')
  with con:
    cur.execute(f"UPDATE SlaveDB set {column} = %s WHERE slaveid = %s AND guildid = %s", (value, member, guild))


def get_badwords(member, guild):
  cur.execute("SELECT word FROM Badwords WHERE slaveid = %s AND guildid = %s", (member, guild))
  badwords = cur.fetchall()
  return badwords


def insert_badword(member, domme, word, guild):
  with con:
    cur.execute(
      "INSERT INTO Badwords (slaveid, dommeid, guildid, word, str_time) VALUES (%(slaveid)s, %(dommeid)s, %(guildid)s, %(badword)s, %(str_time)s)",
      {'slaveid': member,
       'dommeid': domme,
       'guildid': guild,
       'badword': word,
       'str_time': get_time_date()})


def remove_badword(member, word, guild):
  with con:
    cur.execute("DELETE FROM Badwords WHERE slaveid=%(slaveid)s AND word=%(badword)s AND guildid=%(guildid)s",
                {'slaveid': member,
                 'guildid': guild,
                 'badword': word})


def clear_badword(member, guild):
  with con:
    cur.execute("DELETE FROM Badwords WHERE slaveid=%s AND guildid=%s", (member, guild))


def get_slaves(member, guild):
  cur.execute("SELECT slaveid, rank FROM Ownership WHERE ownerid = %s AND guildid = %s ORDER BY rank", (member, guild))
  slaves_list = cur.fetchall()
  return slaves_list


def set_slave_rank(member, rank, guild):
  with con:
    cur.execute("UPDATE Ownership SET rank = %s WHERE slaveid = %s AND guildid = %s", (rank, member, guild))


##############################################################################
#                                                                            #
#                                                                            #
#                                   MONEY                                    #
#                                                                            #
#                                                                            #
##############################################################################

def get_money(member, guild):
  cur.execute("SELECT * FROM Money WHERE memberid = %s AND guildid = %s", (member, guild))
  try:
    data = cur.fetchall()[0]
    return [data[0], data[1], data[2], int(data[3] / 10)]
  except IndexError:
    with con:
      cur.execute("INSERT INTO Money (memberid, guildid, coin, gem) VALUES (%s, %s, %s, %s)", (member, guild, 100, 0))
    return [member, guild, 169, 0]


def add_money(member, guild, coin, gem):
  get_money(member, guild)
  with con:
    cur.execute("UPDATE Money SET coin = coin + %s, gem = gem + %s WHERE memberid = %s AND guildid = %s",
                (coin, gem, member, guild))


def remove_money(member, guild, coin, gem):
  get_money(member, guild)
  with con:
    cur.execute("UPDATE Money SET coin = coin - %s, gem = gem - %s WHERE memberid =%s AND guildid = %s",
                (coin, gem, member, guild))


##############################################################################
#                                                                            #
#                                                                            #
#                                  PRISON                                    #
#                                                                            #
#                                                                            #
##############################################################################


def lock(slave, guild, domme, num, sentence, roles):
  with con:
    cur.execute("DELETE FROM Prison WHERE slaveid = %s AND guildid = %s", (slave, guild))
    cur.execute(
      "INSERT INTO Prison (slaveid, guildid, dommeid, num, sentence, count, roles) VALUES (%s, %s, %s, %s, %s, %s, %s)",
      [slave, guild, domme, num, sentence, 0, roles])


def update_lock(slave, sentence, guild):
  with con:
    cur.execute("UPDATE Prison SET num = num - 1, sentence = %s, count = count + 1 WHERE slaveid = %s AND guildid = %s",
                (sentence, slave, guild))
  coins_to_add = (30 + random.randint(0, 20))
  add_money(slave, guild, coins_to_add, 0)


def get_prisoner(slave, guild):
  cur.execute("SELECT * FROM Prison WHERE slaveid=%s AND guildid =%s", (slave, guild))
  data = cur.fetchall()
  try:
    return data[0]
  except IndexError:
    return


def update_lock_raw(slave, sentence, num, guild):
  with con:
    cur.execute("UPDATE Prison SET num = %s, sentence = %s, WHERE slaveid = %s AND guildid = %s",
                (num, sentence, slave, guild))


def release_prison(slave, guild):
  lines = get_prisoner(slave, guild)[5]
  with con:
    cur.execute("UPDATE SlaveDB SET lines = lines + %s WHERE slaveid = %s AND guildid = %s", (lines, slave, guild))
    cur.execute("SELECT roles FROM Prison WHERE slaveid=%s AND guildid=%s", (slave, guild))
    data = cur.fetchall()[0][0]
    cur.execute("DELETE FROM Prison WHERE slaveid = %s AND guildid = %s", (slave, guild))
  try:
    value = []
    for i in range(int(len(data) / 18)):
      value.append(int(data[i * 18:(i * 18) + 18]))
    return value
  except IndexError:
    return [0]


##############################################################################
#                                                                            #
#                                                                            #
#                                 BLACKLIST                                  #
#                                                                            #
#                                                                            #
##############################################################################


def get_blacklist(guild):
  cur.execute("SELECT memberid FROM Blacklist WHERE guildid = %s", (guild,))
  data = cur.fetchall()
  try:
    data = [d[0] for d in data]
    return data
  except IndexError:
    return []


def insert_remove_blacklist(member, guild):
  if member in get_blacklist(guild):
    with con:
      cur.execute("DELETE FROM Blacklist WHERE memberid = %s AND guildid = %s", (member, guild))
    return False
  else:
    with con:
      cur.execute("INSERT INTO Blacklist (memberid, guildid) VALUES (%s, %s)", (member, guild))
    return True


##############################################################################
#                                                                            #
#                                                                            #
#                                  ESCAPE                                    #
#                                                                            #
#                                                                            #
##############################################################################


def insert_escape(member, guild, safe_time, type):
  with con:
    cur.execute("INSERT INTO Escape (memberid, guildid, timeint, type) VALUES (%s, %s, %s, %s)",
                (member, guild, int(str(time() + (safe_time * 60 * 60))[:10]), type))


def is_escaped(member, guild):
  cur.execute("SELECT * FROM Escape WHERE memberid = %s AND guildid = %s", (member, guild))
  try:
    data = cur.fetchall()[0]
    return data
  except IndexError:
    return


def clear_escape():
  with con:
    cur.execute("DELETE FROM Escape WHERE timeint < %s", (int(str(time())[:10]),))
    cur.execute("DELETE FROM Botban WHERE timeint < %s", (int(str(time())[:10]),))


##############################################################################
#                                                                            #
#                                                                            #
#                              LEADERBORARD                                  #
#                                                                            #
#                                                                            #
##############################################################################


def get_lines_leaderboard(guild):
  cur.execute("SELECT * FROM SlaveDB WHERE guildid = %s ORDER BY lines DESC", (guild,))
  data = cur.fetchall()
  data = [(line[0], line[5]) for line in data if line[5] != 0]
  return data


def get_money_leaderboard(guild):
  cur.execute("SELECT memberid, coin, gem FROM Money WHERE guildid = %s ORDER BY gem DESC, coin DESC", (guild,))
  data = cur.fetchall()
  return data


def get_chess_leaderboard(guild):
  cur.execute("SELECT memberid, point FROM ChessData WHERE guildid = %s ORDER BY point DESC", (guild,))
  data = cur.fetchall()
  return data


##############################################################################
#                                                                            #
#                                                                            #
#                                BOT BAN                                     #
#                                                                            #
#                                                                            #
##############################################################################


def insert_botban(member, ban_till, reason):
  with con:
    cur.execute("INSERT INTO Botban (memberid, timeint, reason) VALUES (%s, %s, %s)",
                (member, int(str(time() + ban_till)[:10]), reason))
    cur.execute("DELETE FROM SlaveDB WHERE slaveid=%s", (member,))
    cur.execute("DELETE FROM Ownership WHERE slaveid=%s", (member,))
    cur.execute("DELETE FROM Ownership WHERE ownerid=%s", (member,))
    cur.execute("DELETE FROM Badwords WHERE slaveid=%s", (member,))
    cur.execute("DELETE FROM Badwords WHERE dommeid=%s", (member,))
    cur.execute("DELETE FROM Worship WHERE memberid=%s", (member,))


def is_botban(member):
  cur.execute("SELECT * FROM Botban WHERE memberid = %s", (member,))
  try:
    data = cur.fetchall()[0]
    return data
  except IndexError:
    return None


##############################################################################
#                                                                            #
#                                                                            #
#                                 CHESS                                      #
#                                                                            #
#                                                                            #
##############################################################################


def insert_chessdata(member, guild):
  with con:
    cur.execute(
      "INSERT INTO ChessData (memberid, guildid, wincount, losecount, drawcount, point, playingwith) VALUES (%s, %s, %s, %s, %s, %s, %s)",
      (member, guild, 0, 0, 0, 0, 0))
  return (member, guild, 0, 0, 0, 0, 0)


def get_chessdata(member, guild):
  cur.execute("SELECT * FROM ChessData WHERE memberid = %s AND guildid = %s", (member, guild))
  try:
    data = cur.fetchall()[0]
    return data
  except IndexError:
    return insert_chessdata(member, guild)


def update_chessdata(member, guild, result, playingwith):
  get_chessdata(member, guild)
  wincount = 0
  losecount = 0
  drawcount = 0
  point = 0
  if result == 1:
    wincount = 1
    point = randint(75, 100)
    playingwith = 0
  elif result == -1:
    losecount = 1
    point = -1 * randint(75, 100)
    playingwith = 0
  elif result == 0:
    drawcount = 1
    point = randint(25, 50)
    playingwith = 0

  with con:
    cur.execute(
      "UPDATE ChessData SET wincount = wincount + %s, losecount = losecount + %s, drawcount = drawcount + %s, point = point + %s, playingwith = %s WHERE memberid = %s AND guildid = %s",
      (wincount, losecount, drawcount, point, playingwith, member, guild))


def dump_chess_game(player, guild, game, endtime):
  with con:
    cur.execute("INSERT INTO ChessMatch (player, guildid, game, endtime) VALUES (%s, %s, %s, %s)",
                (player, guild, game, endtime))


def load_chess_game(player, guild):
  cur.execute("SELECT * FROM ChessMatch WHERE player = %s AND guildid = %s", (player, guild))
  try:
    data = cur.fetchall()[0]
    return data
  except IndexError:
    return


def update_chess_game(player, guild, game, newplayer):
  with con:
    cur.execute("UPDATE ChessMatch SET player = %s, game = %s WHERE player = %s AND guildid = %s",
                (newplayer, game, player, guild))


def delete_chess_game(player, guild):
  with con:
    cur.execute("DELETE FROM ChessMatch WHERE player = %s AND guildid = %s", (player, guild))


def clear_chess_game():
  with con:
    cur.execute("DELETE FROM ChessMatch WHERE endtime < %s", (int(str(time())[:10]),))
