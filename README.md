# ![seductress](seductress_icon.jpg)<br>Seductress (Femdom Discord Bot) 

[![GitHub](https://img.shields.io/static/v1?label=Github&logo=github&message=%20&color=ffffff&style=plastic)](https://github.com/Seductress-5834/Indroduction "GitHub Page")
[![invite](https://img.shields.io/static/v1?label=Bot%20invite&logo=robot&message=here&color=green&style=plastic)](https://bit.ly/3uZ0PNG "Bot Invite link")
[![discord](https://img.shields.io/discord/895203728230064150?color=F2A2C0&label=Seductress%20Support%20Server&logo=discord&logoColor=F2A2C0&style=plastic)](https://discord.gg/9gGJamu2Mk "Join Server")
<br>[![BTC](https://img.shields.io/static/v1?label=BTC&logo=bitcoin&message=39beULEyEDSEoa7VqaqaPinty4MGcujBfM&color=yellow&style=plastic)](BTC.svg "BTC QR Code")
<br>[![ETC](https://img.shields.io/static/v1?label=ETC&logo=ethereum&message=0x97B5dD5D5a0dC15A5798Cb7444CdC2F2884763AA&color=blue&style=plastic)](ETC.svg "ETC QR Code")
___

Seductress is a Discord bot coded in Python with [Discord.py](https://discordpy.readthedocs.io/en/master/api.html "Docs") library.
Mainly NSFW bot with intention to be used in nsfw servers, Bringing BDSM features to Discord especially in Femdom Communities. Commands are desined to simulate gagging Subs, Punishments, and locking in chastity.

Seductress will help Dommes to gag Submissive pets and force them to obey, behave, beg and say "Yes Mistress!"
She will punish and gag them till they break and will rebuild them. Commands are Ideal for following communities: **BDSM, Femdom, pet-play, chastity.**
if You Like Seductress, Please help by donating/support.

## Getting Started🚀
> Bot prefix is **`s.`**

 1. Invite the bot to server. [here](https://bit.ly/3uZ0PNG "Bot Invite link")<br>
 1. Use the Command **`s.setup`** in the server to start initializing. *(required Administrative Permission.)*
 > Note: Domme roles and Sub roles should be made in the server before initializing the Bot.
___

## Features
### Economy
- **how to earn coins**
  - counting in the server gives coins on each count.
  - using the command `s.ruin` you can ruin the count and guess the next correct number, the member who guess the correct number gets 30 coins. *beware of lurkers* 
  - bumping the server will also gives you 30 coins.
  - be active in server every 10 messages in server gives you a coin.
  - using the command `s.lock @mention` **Dommes** can earn 20 coins by locking the subs in the prison.
  - **Subs** can earn coins by writing lines in prison, 15 coins per line.
  - Members can transfer coin to other members by using the command `s.give @mention <amount>`
> *Continue reading to learn more about lock command*
  - **how to earn Gems**
    - **Dommes** earns a gem when a sub simps for her using the command `s.simp @mention`, dommes get 2 gems per simp.
    - **Subs** earns a gem by simping for a domme using the command `s.simp @mention`, subs get 1 gem per 10 simps.
  > *Simping costs 100 coins*

### Ownership

- **Dommes** can own subs in the server by using the command `s.own @mention`, this will make a consent request to the sub to accept.
- **Dommes** can also disown a sub by using the command `s.disown @mention`.

### Gags
- **Dommes** can gag/ungag a sub by using the command `s.gag @mention`, this will convert subs messages into kitty or puppy sounds. if the sub is not owned by the domme then it costs a gem to gag the sub and gag lasts only 10 mins.

### Badwords
- Dommes can **add badwords** to subs by using the command `s.badword @mention <words>`.
- Dommes can **remove badwords** from subs by using the command `s.removeword @mention <words>`.
- Dommes can also **clear all badwords** at once by using the command `s.clearwords @mention`.
- If the sub is not owned by the domme then it costs a gem to **add badword**, but it does not cost a gem to remove/clear badwords from a free sub.
> If a badword is found in sub's message then the messages gets deleted and the sub loses their heart/life. After losing 10 hearts/lifes the sub gets gagged till the owner ungags the sub. if the sub does not have an owner then the sub remains gagged for 30 mins.

### Emoji
- **Dommes** can ban/allow emojis to the sub by using the command `s.emoji @mention`.
- If the sub is not owned by the domme then it costs a gem to ban/allow emojis and it is valid only for an hour.
  
### Chastity lock
- **Dommes** can chastity lock owned sub by using the command `s.chastity @mention`, this will ban the sub from all the channels that are marked as NSFW.
> *Chastity command will not work if the sub is having admin permission in the server*

### Ear muffs
- **Dommes** can give ear muffs to owned subs and prevent them from Connecting to Voice Channels in the server by using the command `s.muffs @mention`
> *Muffs command will not work if the sub is having admin permission in the server*

### Blindfold
- **Dommes** can blindfold owned subs for 5 mins by using the command `s.blind @mention`, during 5 mins sub can't access any channels from the server.  
> *Blind command will not work if the sub is having admin permission in the server*

### Tie
- **Dommes** can tie owned sub to a specific channel in the server by using the command `s.tie @mention #channel`, so the sub can't message in any other channels.
- To untie the sub dommes can use the command `s.untie @mention`

### Nickname
- **Dommes** can change nickname of owned sub by using the command `s.nick @mention <name>`

### Sub Ranking
- If a **Dommes** has more than one subs in the server then she can rank them from favorite sub to least favorite, by the command `s.rank @mention X` *it will be a good tease.*

### NSFW Commands
- Members can use the command `s.porn` to get random femdom/beautiful/ pics.
- Members can also get random femdom porn videos by using the command `s.pornvideo`
  
### Gambling
- Members can bet on **coin-flips** using the command `s.coinflip <heads|tails> <bet amount>`
- Members can also play **roulete** using the command `s.roulete <bet amount>  <space>`

### Lock
- Dommes with permission to lock subs can use the command `s.lock @mention` to lock the subs in prison.
- Subs can write the lines or stay in prison for 2 hours to be free.
- Sub can escape from prison if he posses a gem by using the command `s.escape`
-  Dommes or Admins can unlock the sub from prison by using the command `s.unlock @mention`
> Subs gains some protection from going back to prison.
> - sub gains 12 mins of protection if the sub completes the lines 
> - sub gains 30 mins of protection if the sub waits for 2h and comes out of prison
> - sub gains 6 hours of protection if the sub use the command `s.escape`

### Chat
- Seductress can talk with you, if you wanna talk with seductress use 2 dots/period as prefix of the sentence.
  - example 1 : ```..hi baby girl how are you?```
  - example 2 : ```..what is your fantasy?```

### Actions
- Members can *hug, kiss, cuddle, pat, poke, spank, slap* use the following commands respectively `s.hug @mention`, `s.kiss @mention`, `s.cuddle @mention`, `s.pat @mention`, `s.poke @mention`, `s.spank @mention`, `s.slap @mention`.

### Stats
- Members can use `s.stats` to get server stats.
- Members can use `s.status @mention` to get status of members.
  
### Admin Commads
- Admins can initialize the bot by using the command `s.setup`
  - *Domme roles and Sub roles should be made in the server before initializing the Bot.*

- `s.setNSFW @mentionRole/s` use this command to make sure that only members with mentioned role/s can access NSFW commands.
- `s.setchat @mentionRole/s` Bot will only chat with members with the mentioned role/s to have fun and erp.
- `s.blacklist @mention` this command will add/remove the mentioned member from blacklisted members.
- `s.blacklist` this command will show the list of blacklisted members in the server.
