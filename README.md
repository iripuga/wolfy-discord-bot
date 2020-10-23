# Wolfy
A simple discord bot to help you play werewolfes on discord.

*WARNING!!!* This is **not plug&play** so prepare yourself to do some terminal magic ;). 

# Requirements
- run `pip install discord`
- run `pip install dotenv`
- if you run in issues with ssl certificate try https://stackoverflow.com/questions/62108183/discord-py-bot-dont-have-certificate
    *Basically navigate to your Applications/Python 3.8/ folder and double click the Install Certificates.command.*
- I can't include environment and game data, since they contain private information. To make it work you will need a discord bot and save login credentials(DISCORD_BOT_TOKEN, GUILD_ID, GUILC_CHANNEL_ID) of the bot into .env file. For game you need to make .gameData.json which includes game rules, data about players etc. like demonstrated in .env_example and .gameData_example.json. You can just rename gameData_example.json into .gameData.json and only **add players** as presented in example od 'discord-user-1' from gameData_example.json.

# Authorize wolfy bot to your server...
- create new discord bot on [a link](https://discord.com/login?redirect_to=%2Fdevelopers).
- Go to you new bot application and find DISCORD_BOT_TOKEN under 'Bot' tab. Copy it to .env file.
- From here on you can follow instructions on [a link](https://discordjs.guide/preparations/adding-your-bot-to-servers.html#creating-and-using-your-own-invite-link)

# How to run the bot
1. In wolfy.py add `elif` statement for your discord server like it is presented in the code.
    ```
    elif server.upper() == 'YOUR_GUILD_NAME':
        GUILD = os.getenv('YOUR_GUILD_ID')
        CHANNEL = os.getenv('YOUR_GUILD_CHANNEL_ID')
    ```
2. From git repository run `python wolfy.py`.
3. Enter name of your GUILD into terminal and wait for wolfy to log on. At anytime you can check whether bot is present in guild by typing 'woof' in the channel.

# How to play
To learn all the commands run 'w.help' in discord server and wolfy will send you commands list into direct message. 

*IMPORTANT* All players must turn on their status with 'w.status' command and then one of them starts the game with '.w' command.

Otherwise the game runs according to rules of werewolfes game - [a link](https://www.youtube.com/watch?v=XsP6LvZQpLk). 

Any feedback is welcome. Enjoy.