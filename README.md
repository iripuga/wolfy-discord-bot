# Wolfy
A simple discord bot to help you play werewolfes on discord during quarantine.

**WARNING!!!** This is **not plug&play** so prepare yourself to do some setup steps. 

# Requirements
- run `pip install discord` and `pip install dotenv`
- if you run in issues with ssl certificate try [this thread](https://stackoverflow.com/questions/62108183/discord-py-bot-dont-have-certificate)
    (Basically navigate to your `Applications/Python 3.8/` folder and double click the `Install Certificates.command`.)
- I can't include environment and game data, since they contain private information. To make it work you will need a discord bot and save login credentials(**DISCORD_BOT_TOKEN, GUILD_ID, GUILD_CHANNEL_ID**) of the bot into **.env** file. As a reference use .env_example file.
- For game you also need to generate **.gameData.json** which includes game rules, data about players etc. like demonstrated in .gameData_example.json. You can do that by adding players discord data in **.genGameData.py**(line 9) and then run `python .genGameData.py`.
# Authorize wolfy bot to your server...
- create new discord bot on [developer portal](https://discord.com/login?redirect_to=%2Fdevelopers).
- Go to you new bot application and find DISCORD_BOT_TOKEN under 'Bot' tab. Copy it to **.env** file.
- From here on you can follow instructions on [how to add your discord bot to server](https://discordjs.guide/preparations/adding-your-bot-to-servers.html#creating-and-using-your-own-invite-link)

# How to run the bot
- In wolfy.py add `elif` statement for your discord server like it is presented in the code.
    ```
    elif server.upper() == 'YOUR_GUILD_NAME':
        GUILD = os.getenv('YOUR_GUILD_ID')
        CHANNEL = os.getenv('YOUR_GUILD_CHANNEL_ID')
    ```
- From git repository run `python wolfy.py`.
- Enter name of your GUILD into terminal and wait for wolfy to log on. At anytime you can check whether bot is present in guild by typing `woof` in the channel. You can also call wolfy to another guild by typing `woof`in desired guild.

# How to play
To learn all the commands run `w.help` in discord server and wolfy will send you commands list into direct message. 

*IMPORTANT!* All players must turn on their status with `w.status` command and then one of them starts the game with `.w` command. When game is finished only the person who started the game can finish it with `w.end`.

You can find explanation of werewolfes game rules [here](https://www.youtube.com/watch?v=XsP6LvZQpLk). 

Any feedback is welcome. Enjoy.