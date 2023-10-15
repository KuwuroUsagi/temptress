#!/bin/python3
from discord import Embed

main = Embed(title='Main commands (everybody can use)',
             description=f"**To check the status**\n> **`/status`** this will show your status in the server."
                         f"\n> **`/status @mention`**  this will show the status of the mentioned member in the server."
                         f"\n> **`/stats`** this command will show my stats/configs in the server."
                         f"\n> **`/bal`** this command will show your coins and gems"
                         f"\n> **`/<action> @mention`** actions can be **`hug`**, **`cuddle`**, **`pat`**, **`kiss`**, **`slap`**, **`spank`**. *For example: __/hug @mention__*"
                         f"\n> **`/define <word>`** this command will show the definition of the word from urban dictionary."
                         f"\n\n> __Chat Commands__ ([click for docs](https://github.com/Zero6992/chatGPT-discord-bot))"
                         f"\n> **`/chat [message]`** Chat with ChatGPT!"
                         f"\n> **`/switchpersona [persona]`** Switch between optional ChatGPT jailbreaks. The list will be shown when you use the command."
                         f"\n> **`/private`** ChatGPT switch to private mode"
                         f"\n> **`/public`** ChatGPT switch to public mode"
                         f"\n> **`/reset`** Clear ChatGPT conversation history",

             color=0x9479ED)

nsfw = Embed(title='NSFW commands',
             description=f"> **`/porn`** this command will show you irl femdom Pics in server."
                         f"\n> **`/pornvideo`** this command will send you a femdom porn suggestion.:wink: :drool:"
                         f"\n> **`/pornhub <tag>`** this command will show you a porn suggestion in a category.",
             color=0x9479ED)

domme = Embed(title='Domme only commands', color=0x9479ED)

domme.add_field(name="To own or disown a sub.",
                value="> **`/own @mention`** this prompts the mentioned user for consent to become a sub for the Domme using this command."
                      "\n> **`/disown @mention`**  this removes the mentioned user as a sub of the Domme using this command.\n",
                inline=False)

domme.add_field(name="To Gag Subs", value="> **`/gag @mention`** this will gag the sub and dommes can have fun."
                                          "\n**Note: If the sub is not owned by Domme then gag costs a gem. (valid for 10 mins)**\n",
                inline=False)

domme.add_field(name="To Chastity lock Subs",
                value="> **`/chastity @mention`** this command will block NSFW channels from the sub."
                      "\n**Note: Dommes have to own a sub before locking a sub in chastity.**\n", inline=False)

domme.add_field(name="To ear muffs Subs",
                value="> **`/muffs @mention`** this command will block voice channels from the sub."
                      "\n**Note: Dommes have to own a sub before blocking Voice Channels.**\n", inline=False)

domme.add_field(name="To blind Subs",
                value="> **`/blind @mention`** this command will block **All Channels** from the sub for 5 minutes."
                      "\n**Note: Dommes have to own a sub before blocking All Channels and this command has cooldown.**\n",
                inline=False)

domme.add_field(name="To add and remove badwords",
                value="> **`/badword @mention <word>`** this will add the word as a badword, preventing the sub from using the word again."
                      "\n> **`/removeword @mention <word>`**  this will remove the word from the sub's list of badwords."
                      "\n> **`/clearwords @mention`** this will clear the sub's list of badwords."
                      "\n**Note: If sub is not owned by a Domme then adding a badword will cost gems.**\n\n\n",
                inline=False)

domme.add_field(name="To change Nickname of the sub.",
                value="> **`/nickname @mention <name>`**  this will change the nickname of the sub in the server."
                      "\n> **`/nickname @mention`** this will remove the nickname of the sub in the server."
                      "\n**Note: Dommes must own the sub or sub should consent to have his/her name changed by Dommes.**\n",
                inline=False)

domme.add_field(name="To enable and disable emoji of the sub.",
                value="> **`/emoji @mention`** using this command you can toggle the sub permission to use emojis in the server."
                      "\n**Note: If the sub is not owned by a Dommes then this command costs a gem. (emoji ban is valid only for an hour)**\n\n\n",
                inline=False)

domme.add_field(name="To tie a sub in specific text channel in server.",
                value="> **`/tie @mention #channel`** this will only allow the sub to send messages in the specified text channel."
                      "\n> **`/untie @mention`** this will allow the sub to send messages normally."
                      "\n**Note: Dommes must own the sub before using tie and untie commands.**\n\n\n", inline=False)

domme.add_field(name="To rank your sub in hierarchy.",
                value="> **`/rank @mention X`** X is a rank given to your owned subs."
                      "\n**Note: Dommes must own the sub before using rank command.**\n\n\n", inline=False)

lock = Embed(title=' How to use prison?',
             description=f"The command to put subs in prison is `/lock @mention` as per example \"**`/lock @name#0001`**\". "
                         f"Then you just need to choose the punishment of the sub if it is 'degree' or 'worship' and finally choose the level of torture "
                         f"easy will make the sub write from 2-3 lines, medium will make the sub write 3-5 lines, hard will make the sub write 7-10 lines. After it just enjoy the sub punishment!"
                         f"\n\n\n**Only the Domme who locked can unlock the sub, ||and admins for safety reasons||**"
                         f"\n> **`/unlock @mention`** this will unlock the sub from prison."
                         f"\n**NOTE: Admins can remove sub from prison just by removing prison role. deleting of the role or prison channel will unlock all the subs from prison.**",
             color=0x9479ED)

admin = Embed(title='Admin commands',
              description=f"> **`/setup`** to configure me in the server."
                          f"\n> **`/setNSFW @mentionRoles`** this will make sure that only people with mentioned role can access NSFW commands."
                          f"\n> **`/setchat @mentionRoles`** I will chat with member only with the mentioned roles and have fun. ||maybe some erp||"
                          f"\n> **`/setcount #channel`** this command will set the  mentioned channel as counting channel."
                          f"\n> **`/blacklist @mention`** This will blacklist a mentioned member, and prevent them to lock any subs."
                          f"\n> **`/blacklist`** this will show the list of blacklisted members in the server.",
              color=0x9479ED)

games = Embed(title='Games',
              description=  # f"> **`/chess @mention`** this command will challenges the mentioned member"
              # f"\n> **`/resign`** to resign playing chess and accept your defeat"
              f"\n> **`/coinflip <head|tail> <bet amount>`** gamble and earn coins by flipping coins"
              f"\n> **`/roulete <bet amount> <space>`** gamble and coins by playing roulete"
              f"\n> **`/rps @mention <bet amount>`** play rock paper scissors and steal coins from them.",
              color=0x9479ED)
