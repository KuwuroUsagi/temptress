import database

def who_is(author, member):
  """
  returns int depends on relationship between author and member.

  2       author and member is the same person + has domme/switch role

  202     both author and member have domme/switch role

  200     member is owned by author

  201     member is unowned by author

  >300    discord id of member's owner

  222     member does not have domme/switch or slave role and author has domme/switch role

  1       author and member is the same person + has slave role

  101     both author and member have slave role

  102     author has slave role and member has domme/switch role

  103     member is a switch, author is a slave

  111     member does not have domme/switch or slave role and author has slave role

  0       author does not have both slave and domme/switch role

  -1      member is bot banned

  <-1     unixtime till author is banned
  """
  member_has_role = lambda rid: str(rid) in [str(role.id) for role in member.roles]
  author_has_role = lambda rid: str(rid) in [str(role.id) for role in author.roles]

  domme = database.get_config('domme', member.guild.id)[0]
  sub = database.get_config('slave', member.guild.id)[0]
  switch = database.get_config('switch', member.guild.id)[0]

  print(f"""{author_has_role(domme)=} | {author_has_role(sub)=} | {author_has_role(switch)=}
  {member_has_role(domme)=} | {member_has_role(sub)=} | {member_has_role(switch)=}""")

  # banned
  ban_data = database.is_botban(author.id)

  if ban_data is not None:
    return -1 * ban_data[1]

  if database.is_botban(member.id) is not None:
    return -1

  # relationship

  if author_has_role(domme) or author_has_role(switch):  # author is domme / switch
    if author.id == member.id:
      return 2  # allowed to do the action but not on yourself

    if member_has_role(domme):
      return 202  # allowed to do but not on another domme

    if member_has_role(sub) or member_has_role(switch):
      ownerid = database.get_owner(member.id, member.guild.id)

      if ownerid == 0:
        return 201  # member is unowned by author

      if author.id in ownerid:
        return 200  # member is owned by author
      else:
        return 301  # member is owned by someone else

    return 222  #/ member has no controlling roles slave/switch/domme and author has domme/switch

  elif author_has_role(sub):
    if author.id == member.id:
      return 1  # not allowed to do the action, and obviously not on yourself

    if member_has_role(switch):
      return random.choice([101, 102])  # member is a switch

    if member_has_role(sub):
      return 101  # both are slave

    if member_has_role(domme):
      return 102  # member is a domme, author is a slave


    else:

      return 111  # member has no controlling roles slave/switch/domme and author has slave

  return 0  # author has no controlling roles slave/switch/domme