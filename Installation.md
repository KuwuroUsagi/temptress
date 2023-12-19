# Temptress Bot Installtion

## 📩 Install files

1. Download the code from github / wherever
2. Unzip

## 🐍 Download Python

- Download Python 3.9
  from [https://www.python.org/downloads/release/python-390/](https://www.python.org/downloads/release/python-390/#:~:text=Full%20Changelog-,Files,-Version)

    - If you are using Windows 64bit download `Windows x86-64 executable installer`.

- During the installlation make sure to check `Add Python 3.9 to PATH`.

## 📂 Install Libraries

- Open the terminal/cmd in the folder where you unzipped the code.
- Run whichever works for you:
    - `pip install -r requirements.txt`
    - `python -m pip install -r requirements.txt`

## 🔮 Set up Postgresql Database

- I am personally using PGAdmin 4 for this, but if you know better do yours.
- Either way, you need to create a database called 'temptress' and put the credentials in the `config.ini` file.

### Setup database using PGAdmin 4 (recommended)

- Download PGAdmin for your OS from https://www.pgadmin.org/download/
- Set it up, when you pick a password, put it in `config.ini` instead of `<PUT DATABSE PASSWORD HERE>
- I will assume (since default) that the username is `postgres`, but if it isn't update it in `config.ini`
- Create a database called `temptress`

## 🍡 Get Discord Bot Token

- Go to https://discordapp.com/developers and create a new application.
- Go to the `Bot` tab, click **Add Bot**.
- Click **Reset Token** and copy the new token
- Put the token in `config.ini` instead of `<PUT DISCORD TOKEN HERE>` 
- Under *Privileged Gateway Intents* check all the boxes like so:
  ![https://i.imgur.com/4yjNqJB.png](https://i.imgur.com/4yjNqJB.png)
- Go to the `OAuth2` -> `URL Generator` tab
  - Select **bot** in the `scopes`, then **Administrator** and open generated URL to add the bot.

## ▶️ Run the bot

Finally, open the terminal/cmd in the bot's folder and type:
```shell
python main.py
```

This should run the bot.