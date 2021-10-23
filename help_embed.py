#!/bin/python3
from discord import Embed


main = Embed(title='Main commands (everybody can use)',
             description=f"**To check the status**\n> **`s.status`** this will show your status in the server."
             f"\n> **`s.status @mention`**  this will show the status of the mentioned member in the server."
             f"\n> **`s.stats`** this command will show my stats/configs in the server."
             f"\n> **`s.action @mention`** actions can be **`hug`**, **`cuddle`**, **`pat`**, **`kiss`**, **`poke`**, **`slap`**, **`spank`**",
             color=0x9479ED)

nsfw = Embed(title='NSFW commands',
             description=f"> **`s.porn`** this command will show you irl femdom Pics in server."
             f"\n> **`s.pornvideo`** this command will send you a femdom porn suggestion.:wink: :drool:"
             f"\n> **`s.pornhub <femdom lesbians>`** you can search videos from pornhub. **`s.ph`** for short.",
             color=0x9479ED)

domme = Embed(title='Domme only commands', color=0x9479ED)

domme.add_field(name="To own or disown a sub.", value="> **`s.own @mention`** this prompts the mentioned user for consent to become a sub for the Domme using this command."
                "\n> **`s.disown @mention`**  this removes the mentioned user as a sub of the Domme using this command.\n", inline=False)

domme.add_field(name="To Gag Subs", value="> **`s.gag @mention`** this will gag the sub and have fun."
                "\n**Note: Dommes have to own a sub before before converting a sub into a puppy or kitty.**\n", inline=False)

domme.add_field(name="To Chastity lock Subs", value="> **`s.chastity @mention`** this command will block NSFW channels from the sub."
                "\n**Note: Dommes have to own a sub before locking a sub in chastity.**\n", inline=False)

domme.add_field(name="To ear muffs Subs", value="> **`s.muffs @mention`** this command will block voice channels from the sub."
                "\n**Note: Dommes have to own a sub before blocking Voice Channels.**\n", inline=False)

domme.add_field(name="To blind Subs", value="> **`s.blind @mention`** this command will block **All Channels** from the sub for 5 minutes."
                "\n**Note: Dommes have to own a sub before blocking All Channels and this command has cooldown.**\n", inline=False)

domme.add_field(name="To add and remove badwords",
                value="> **`s.badword @mention <word>`** this will add the word as a badword, preventing the sub from using the word again."
                "\n> **`s.removeword @mention <word>`**  this will remove the word from the sub's list of badwords."
                "\n> **`s.clearwords @mention`** this will clear the sub's list of badwords."
                "\n**Note: Dommes have to own a sub first before adding or removing badwords.**\n\n\n",
                inline=False)

domme.add_field(name="To change Nickname of the sub.",
                value="> **`s.nickname @mention <name>`**  this will change the nickname of the sub in the server."
                "\n> **`s.nickname @mention`** this will remove the nickname of the sub in the server."
                "\n**Note: Dommes must own the sub or sub should consent to have his/her name changed by Dommes.**\n",
                inline=False)

domme.add_field(name="To enable and disable emoji of the sub.", value="> **`s.emoji @mention`** using this command you can toggle the sub permission to use emojis in the server."
                "\n**Note: Dommes must own the sub to manage their emojis.**\n\n\n", inline=False)

domme.add_field(name="To tie a sub in specific text channel in server.", value="> **`s.tie @mention #channel`** this will only allow the sub to send messages in the specified text channel."
                "\n> **`s.untie @mention`** this will allow the sub to send messages normally."
                "\n**Note: Dommes must own the sub before using tie and untie commands.**\n\n\n", inline=False)


domme.add_field(name="To rank your sub in hierarchy.", value="> **`s.rank @mention X`** X is a rank given to your owned subs."
                "\n**Note: Dommes must own the sub before using rank command.**\n\n\n", inline=False)

lock = Embed(title=' How to use prison?',
             description=f"The command to put subs in prison is `s.lock @mention` as per example \"**`s.lock @alex#0001`**\". "
             f"Then you just need to choose the punishment of the sub if it is 'degree' or 'worship' and finally choose the level of torture "
             f"easy will make the sub write from 2-3 lines, medium will make the sub write 3-5 lines, hard will make the sub write 7-10 lines. After it just enjoy the sub punishment!"
             f"\n\n\n**Only the Domme who locked can unlock the sub, ||and admins for safety reasons||**"
             f"\n> **`s.unlock @mention`** this will unlock the sub from prison."
             f"\n**NOTE: Admins can remove sub from prison just by removing prison role. deleting of the role or prison channel will unlock all the subs from prison.**",
             color=0x9479ED)


admin = Embed(title='Admin commands',
              description=f"> **`s.setup`** to configure me in the server."
              f"\n> **`s.setNSFW @mentionRoles`** this will make sure that only people with mentioned role can access NSFW commands."
              f"\n> **`s.setchat @mentionRoles`** I will chat with member only with the mentioned roles and have fun. ||maybe some erp||"
              f"\n> **`s.setcount #channel`** this command will set the  mentioned channel as counting channel."
              f"\n> **`s.blacklist @mention`** This will blacklist a mentioned member, and prevent them to lock any subs."
              f"\n> **`s.blacklist`** this will show the list of blacklisted members in the server.",
              color=0x9479ED)
