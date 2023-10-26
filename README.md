# Miss Valentina <br> (Femdom Discord Bot)

___

Miss Valentina is a fork of Seductress, a Discord bot coded in Python
with [Discord.py](https://discordpy.readthedocs.io/en/master/api.html "Docs") library.
Mainly NSFW bot with intention to be used in nsfw servers, Bringing BDSM features to Discord especially in Femdom
Communities. Commands are desined to simulate gagging Subs, Punishments, and locking in chastity.

Miss Valentina will help Dommes to gag Submissive pets and force them to obey, behave, beg and say "Yes Mistress!"
She will punish and gag them till they break and will rebuild them. Commands are Ideal for following communities: *
*BDSM, Femdom, pet-play, chastity.**

## Getting Started🚀

> Bot prefix is **`t.`**

1. Invite the bot to server.(Removed invite, as the bot is depreceated and needs a rewrite)<br>
2. Use the Command **`t.setup`** in the server to start initializing. *(required Administrative Permission.)*

> Note: Domme roles and Sub roles should be made in the server before initializing the Bot.

3. For support join the Discord: https://discord.gg/4bQguQW4eG  (ie. Removing an owner from someone or resetting a
   currency to an amount etc.)
4. If you enjoy the bot and want to see updates and improvements please consider contributing either via a pull request
   or donating for getting developers to work on Miss Valentina! https://ko-fi.com/kuwurousagi

___

## Features

### Economy

- **how to earn coins**
    - counting in the server gives coins on each count.
    - using the command `t.ruin` you can ruin the count and guess the next correct number, the member who guess the
      correct number gets 30 coins. *beware of lurkers*
    - bumping the server will also gives you 30 coins.
    - be active in server every 10 messages in server gives you a coin.
    - using the command `t.lock @mention` **Dommes** can earn 20 coins by locking the subs in the prison.
    - **Subs** can earn coins by writing lines in prison, 15 coins per line.
    - Members can transfer coin to other members by using the command `t.give @mention <amount>`

> *Continue reading to learn more about lock command*

- **how to earn Gems**
    - **Dommes** earns a gem when a sub simps for her using the command `t.simp @mention`, dommes get 2 gems per simp.
    - **Subs** earns a gem by simping for a domme using the command `t.simp @mention`, subs get 1 gem per 10 simps.

> *Simping costs 100 coins*

### Ownership

- **Dommes** can own subs in the server by using the command `t.own @mention`, this will make a consent request to the
  sub to accept.
- **Dommes** can also disown a sub by using the command `t.disown @mention`.

### Gags

- **Dommes** can gag/ungag a sub by using the command `t.gag @mention`, this will convert subs messages into kitty or
  puppy sounds. if the sub is not owned by the domme then it costs a gem to gag the sub and gag lasts only 10 mins.

### Badwords

- Dommes can **add badwords** to subs by using the command `t.badword @mention <words>`.
- Dommes can **remove badwords** from subs by using the command `t.removeword @mention <words>`.
- Dommes can also **clear all badwords** at once by using the command `t.clearwords @mention`.
- If the sub is not owned by the domme then it costs a gem to **add badword**, but it does not cost a gem to
  remove/clear badwords from a free sub.

> If a badword is found in sub's message then the messages gets deleted and the sub loses their heart/life. After losing
> 10 hearts/lifes the sub gets gagged till the owner ungags the sub. if the sub does not have an owner then the sub
> remains gagged for 30 mins.

### Emoji

- **Dommes** can ban/allow emojis to the sub by using the command `t.emoji @mention`.
- If the sub is not owned by the domme then it costs a gem to ban/allow emojis and it is valid only for an hour.

### Chastity lock

- **Dommes** can chastity lock owned sub by using the command `t.chastity @mention`, this will ban the sub from all the
  channels that are marked as NSFW.

> *Chastity command will not work if the sub is having admin permission in the server*

### Ear muffs

- **Dommes** can give ear muffs to owned subs and prevent them from Connecting to Voice Channels in the server by using
  the command `t.muffs @mention`

> *Muffs command will not work if the sub is having admin permission in the server*

### Blindfold

- **Dommes** can blindfold owned subs for 5 mins by using the command `t.blind @mention`, during 5 mins sub can't access
  any channels from the server.

> *Blind command will not work if the sub is having admin permission in the server*

### Tie

- **Dommes** can tie owned sub to a specific channel in the server by using the command `t.tie @mention #channel`, so
  the sub can't message in any other channels.
- To untie the sub dommes can use the command `t.untie @mention`

### Nickname

- **Dommes** can change nickname of owned sub by using the command `t.nick @mention <name>`

### Sub Ranking

- If a **Dommes** has more than one subs in the server then she can rank them from favorite sub to least favorite, by
  the command `t.rank @mention X` *it will be a good tease.*

### NSFW Commands

- Members can use the command `t.porn` to get random femdom/beautiful/ pics.
- Members can also get random femdom porn videos by using the command `t.pornvideo`

### Gambling

- Members can bet on **coin-flips** using the command `t.coinflip <heads|tails> <bet amount>`
- Members can also play **roulete** using the command `t.roulete <bet amount>  <space>`

### Lock

- Dommes with permission to lock subs can use the command `t.lock @mention` to lock the subs in prison.
- Subs can write the lines or stay in prison for 2 hours to be free.
- Sub can escape from prison if he posses a gem by using the command `t.escape`
- Dommes or Admins can unlock the sub from prison by using the command `t.unlock @mention`

> Subs gains some protection from going back to prison.
> - sub gains 12 mins of protection if the sub completes the lines
> - sub gains 30 mins of protection if the sub waits for 2h and comes out of prison
> - sub gains 6 hours of protection if the sub use the command `t.escape`

### Chat

- Miss Valentina can talk with you, if you wanna talk with Miss Valentina use 2 dots/period as prefix of the sentence.
    - example 1 : ```..hi baby girl how are you?```
    - example 2 : ```..what is your fantasy?```

### Actions

- Members can *hug, kiss, cuddle, pat, poke, spank, slap* use the following commands
  respectively `t.hug @mention`, `t.kiss @mention`, `t.cuddle @mention`, `t.pat @mention`, `t.poke @mention`, `t.spank @mention`, `t.slap @mention`.

### Stats

- Members can use `t.stats` to get server stats.
- Members can use `t.status @mention` to get status of members.

### Admin Commads

- Admins can initialize the bot by using the command `t.setup`
    - *Domme roles and Sub roles should be made in the server before initializing the Bot.*

- `/setNSFW @mentionRole/s` use this command to make sure that only members with mentioned role/s can access NSFW
  commands.
- `/setchat @mentionRole/s` Bot will only chat with members with the mentioned role/s to have fun and erp.
- `/blacklist @mention` this command will add/remove the mentioned member from blacklisted members.
- `/blacklist` this command will show the list of blacklisted members in the server.
