#!/bin/python3
import psycopg2
from os import environ
from time import time
from collections import Counter


# DATABASE_URL = 'postgres://okqizptclrjlkj:252b7f77db58686cd92a4e69312fc44fcd2a2035d7b0b049439cf9d741bfe529@ec2-176-34-116-203.eu-west-1.compute.amazonaws.com:5432/d9qu5utgkc6r5d'
# con = psycopg2.connect(DATABASE_URL)
con = psycopg2.connect(environ['DATABASE_URL'])
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
        (name text, guildid bigint, value text)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS SlaveDB
        (slaveid bigint, guildid bigint, gag text, tiechannel bigint, emoji boolean, lines integer)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Ownership
        (slaveid bigint, guildid bigint, ownerid bigint, rank integer, str_time text)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Badwords
        (slaveid bigint, guildid bigint, word text, str_time text)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Prison
        (slaveid bigint, guildid bigint, dommeid bigint, num integer, sentence text, count integer, roles text)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Blacklist
        (memberid bigint, guildid bigint)""")


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
        cur.execute("UPDATE Config SET value = value || %s WHERE name = %s AND guildid = %s", (str(value), name, int(guild)))


def clear_config(name, guild):
    with con:
        cur.execute("DELETE FROM Config WHERE name = %s AND guildid = %s", (name, int(guild)))


def get_config(name, guild):
    try:
        cur.execute("SELECT value FROM Config WHERE name =%s AND guildid = %s", (name, int(guild)))
        value = []
        data = cur.fetchall()[0][0]
        for i in range(int(len(data) / 18)):
            value.append(int(data[i * 18:(i * 18) + 18]))
        return value
    except IndexError:
        return [0]


def remove_guild(guild):
    with con:
        cur.execute("DELETE FROM Config WHERE guildid = %s", (guild,))
        cur.execute("DELETE FROM SlaveDB WHERE guildid = %s", (guild,))
        cur.execute("DELETE FROM Ownership WHERE guildid = %s", (guild,))
        cur.execute("DELETE FROM Badwords WHERE guildid = %s", (guild,))
        cur.execute("DELETE FROM Prison WHERE guildid = %s", (guild,))

##############################################################################
#                                                                            #
#                                                                            #
#                                  FEMDOM                                    #
#                                                                            #
#                                                                            #
##############################################################################


def insert_slave_to_DB(member, guild):
    with con:
        cur.execute("INSERT INTO SlaveDB (slaveid, guildid, gag, tiechannel, emoji, lines) VALUES (%s, %s, %s, %s, %s, %s)", (member, guild, 'off', 0, True, 0))
    return [(member, guild, 'off', 0, True, 0)]


def remove_member(member, guild):
    with con:
        cur.execute("DELETE FROM SlaveDB WHERE slaveid=%s AND guildid = %s", (member, guild))
        cur.execute("DELETE FROM Ownership WHERE slaveid=%s AND guildid = %s", (member, guild))
        cur.execute("DELETE FROM Ownership WHERE ownerid=%s AND guildid = %s", (member, guild))
        cur.execute("DELETE FROM Badwords WHERE slaveid=%s AND guildid = %s", (member, guild))
        cur.execute("DELETE FROM Prison WHERE slaveid=%s AND guildid = %s", (member, guild))


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
        cur.execute("INSERT INTO Ownership (slaveid, guildid, ownerid, rank, str_time) VALUES (%(slaveid)s, %(guildid)s, %(ownerid)s, %(rank)s, %(str_time)s)",
                    {'slaveid': slave,
                     'guildid': guild,
                     'ownerid': owner,
                     'rank': 1000,
                     'str_time': get_time_date()})


def disown_a_slave(member, guild):
    with con:
        cur.execute("DELETE FROM Ownership WHERE slaveid = %s AND guildid = %s", (member, guild))
        cur.execute("DELETE FROM Badwords WHERE slaveid = %s AND guildid = %s", (member, guild))
        cur.execute("UPDATE SlaveDB set gag=%s, tiechannel=%s, emoji=%s WHERE slaveid=%s AND guildid = %s", ['off', 0, True, member, guild])


def update_slaveDB(member, column, value, guild):
    with con:
        cur.execute(f"UPDATE SlaveDB set {column} = %s WHERE slaveid = %s AND guildid = %s", (value, member, guild))


def get_badwords(member, guild):
    cur.execute("SELECT word FROM Badwords WHERE slaveid = %s AND guildid = %s", (member, guild))
    badwords = cur.fetchall()
    return badwords


def insert_badword(member, word, guild):
    with con:
        cur.execute("INSERT INTO Badwords (slaveid, guildid, word, str_time) VALUES (%(slaveid)s, %(guildid)s, %(badword)s, %(str_time)s)", {'slaveid': member,
                                                                                                                                             'guildid': guild,
                                                                                                                                             'badword': word,
                                                                                                                                             'str_time': get_time_date()})


def remove_badword(member, word, guild):
    with con:
        cur.execute("DELETE FROM Badwords WHERE slaveid=%(slaveid)s AND word=%(badword)s AND guildid=%(guildid)s", {'slaveid': member,
                                                                                                                    'guildid': guild,
                                                                                                                    'badword': word})


def clear_badword(member, guild):
    with con:
        cur.execute("DELETE FROM Badwords WHERE slaveid=%s AND guildid=%s", (member, guild))


# def get_task_count(member):
#     cur.execute("SELECT * FROM Tasks WHERE rate NOT IN ('fail') AND slaveid = %s", (member,))
#     return len(cur.fetchall())


# def get_member_tasks(member):
#     cur.execute("SELECT * FROM Tasks WHERE slaveid=%s or dommeid=%s ORDER BY str_time DESC", (member, member))
#     data = cur.fetchall()
#     return data


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
#                              LEADERBORARD                                  #
#                                                                            #
#                                                                            #
##############################################################################


def get_lines_leaderboard(guild):
    cur.execute("SELECT * FROM SlaveDB WHERE guildid = %s ORDER BY lines DESC", (guild,))
    data = cur.fetchall()
    data = [(line[0], line[5]) for line in data if line[5] != 0]
    return data


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
        cur.execute("INSERT INTO Prison (slaveid, guildid, dommeid, num, sentence, count, roles) VALUES (%s, %s, %s, %s, %s, %s, %s)", [slave, guild, domme, num, sentence, 0, roles])


def update_lock(slave, sentence, guild):
    with con:
        cur.execute("UPDATE Prison SET num = num - 1, sentence = %s, count = count + 1 WHERE slaveid = %s AND guildid = %s", (sentence, slave, guild))


def get_prisoner(slave, guild):
    cur.execute("SELECT * FROM Prison WHERE slaveid=%s AND guildid =%s", (slave, guild))
    data = cur.fetchall()
    return data[0]


def release_prison(slave, guild):
    lines = get_prisoner(slave, guild)[5]
    with con:
        cur.execute("UPDATE SlaveDB set lines = lines + %s WHERE slaveid = %s AND guildid = %s", (lines, slave, guild))
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
            cur.execute("DELETE FROM Blacklist WHERE memberid = %s and guildid = %s", (member, guild))
        return False
    else:
        with con:
            cur.execute("INSERT INTO Blacklist (memberid, guildid) VALUES (%s, %s)", (member, guild))
        return True
