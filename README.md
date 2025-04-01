# Minecraft Server Launcher with NGROK Port Forwarding
**Note: You need to add generate and authtoken and also have TCP endpoint before proceeding. Use this link on how to do that.**
[How to setup NGROK for Minecraft Hosting](https://medium.com/@gvarshithreddy8/how-to-create-ngrok-account-for-minecraft-server-hosting-without-touching-the-router-settings-e62977f801fb)

## Step 1: Clone this repository
'''
git clone https://github.com/gvarshithreddy/Minecraft-Launcher.git
'''
## Step 2: Open terminal and run the server_launcher.py
'''
python server_launcher.py
''
## Step 3: Click on start server
A gui will be opened in which you will find "Start Minecraft server" button, click on it
also click on Start Ngrok Server, you will find forwarding address like this
Forwarding                    tcp://ab.bcd.kj.ngrok.io:12349 -> localhost:25565   

**Copy the part after tcp:// till the arrow** and share it to your friends. That's it, enjoy