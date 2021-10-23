#!/bin/python3
import psycopg2
from os import environ
from time import time


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
        (slaveid bigint, guildid bigint, gag text, tiechannel bigint, emoji boolean, lines integer, chastity boolean, muff boolean)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Ownership
        (slaveid bigint, guildid bigint, ownerid bigint, rank integer, str_time text)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Badwords
        (slaveid bigint, guildid bigint, word text, str_time text)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Prison
        (slaveid bigint, guildid bigint, dommeid bigint, num integer, sentence text, count integer, roles text)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Blacklist
        (memberid bigint, guildid bigint)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Money
        (memberid bigint, guildid bigint, coin bigint, gem bigint)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Worship
        (memberid bigint, guildid bigint, simp text)""")


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
        for i in range(1 if (int(len(data) / 18)) == 0 else int(len(data) / 18)):
            if len(data) < 18:
                value.append(int(data))
            else:
                value.append(int(data[i * 18:(i * 18) + 18]))
        return value
    except IndexError:
        return [0]


def get_config_raw(name, guild):
    try:
        cur.execute("SELECT value FROM Config WHERE name =%s AND guildid =%s", (name, guild))
        raw_value = cur.fetchall()[0][0]
        return raw_value
    except IndexError:
        return


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
        #                                 WORSHIP                                    #
        #                                                                            #
        #                                                                            #
        ##############################################################################


def simp(member, guild, women):
    cur.execute("SELECT * FROM Worship WHERE memberid = %s AND guildid = %s", (member, guild))
    data = cur.fetchall()
    if data == []:
        with con:
            cur.execute("INSERT INTO Worship (memberid, guildid, simp) VALUES (%s, %s, %s)", (member, guild, str(women) + '_1'))
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
                cur.execute("UPDATE Worship SET simp = simp || %s WHERE memberid = %s AND guildid = %s", ('/' + str(women) + '_1', member, int(guild)))


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
        cur.execute("INSERT INTO SlaveDB (slaveid, guildid, gag, tiechannel, emoji, lines, chastity, muff) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (member, guild, 'off', 0, True, 0, True, True))
    return [(member, guild, 'off', 0, True, 0, True, True)]


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
        cur.execute("UPDATE SlaveDB set gag=%s, tiechannel=%s, emoji=%s, chastity=%s, muff=%s WHERE slaveid=%s AND guildid = %s", ['off', 0, True, True, True, member, guild])


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
        cur.execute("UPDATE Money SET coin = coin + %s, gem = gem + %s WHERE memberid = %s AND guildid = %s", (coin, gem, member, guild))


def remove_money(member, guild, coin, gem):
    get_money(member, guild)
    with con:
        cur.execute("UPDATE Money SET coin = coin - %s, gem = gem - %s WHERE memberid =%s AND guildid = %s", (coin, gem, member, guild))


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
    add_money(slave, guild, 2, 0)


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
