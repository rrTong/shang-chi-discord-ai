from keep_alive import keep_alive

# the os module helps us access environment variables
# i.e., our API keys
import os

# these modules are for querying the Hugging Face model
import json
import requests

# the Discord Python API
import discord

# regex for discord.content matching
import re

# this is my Hugging Face profile link
API_URL = 'https://api-inference.huggingface.co/models/rrtong/'

# random response for when bot is down
import random
from shang_chi_responses import responses

class MyClient(discord.Client):
    def __init__(self, model_name):
        super().__init__()
        self.api_endpoint = API_URL + model_name
        # retrieve the secret API token from the system environment
        huggingface_token = os.environ['HUGGINGFACE_TOKEN']
        # format the header in our request to Hugging Face
        self.request_headers = {
            'Authorization': 'Bearer {}'.format(huggingface_token)
        }

    def query(self, payload):
        """
        make request to the Hugging Face model API
        """
        data = json.dumps(payload)
        response = requests.request('POST',
                                    self.api_endpoint,
                                    headers=self.request_headers,
                                    data=data)
        ret = json.loads(response.content.decode('utf-8'))
        return ret

    async def on_ready(self):
        # print out information when the bot wakes up
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        # send a request to the model without caring about the response
        # just so that the model wakes up and starts loading
        self.query({'inputs': {'text': 'Hello!'}})

    async def on_message(self, message):
        """
        this function is called whenever the bot sees a message in a channel
        """
        regex = fr"{self.user.id}|xu|shang|chi|shaun|shawn|sean|徐|尚|氣|气|気|シャン|チー|샹|치|Шан|Чи|شانج|شي|legend|傳奇|传奇|伝説|ring|環|环|リング|wenwu|文|武|katy|xialing|夏|靈|灵|dragon|龍|龙|竜|master|師父|师父|師匠|kung\s*fu|功夫|ta\s*lo|大羅|大罗|🐉|🐲|💍"
        # ignore the message if it comes from the bot itself
        if message.author.id == self.user.id:
            return

        if any(re.findall(regex, message.content, re.IGNORECASE)):
          
          # form query payload with the content of the message
          payload = {'inputs': {'text': message.content}}

          # while the bot is waiting on a response from the model
          # set the its status as typing for user-friendliness
          async with message.channel.typing():
            response = self.query(payload)
          bot_response = response.get('generated_text', None)
          
          # we may get ill-formed response if the model hasn't fully loaded
          # or has timed out
          if not bot_response:
              if 'error' in response:
                # bot_response = '`Error: {}`'.format(response['error'])
                bot_response = random.choice(responses)
              else:
                  bot_response = 'Hmm... something is not right.'

          # send the model's response to the Discord channel
          await message.channel.send(bot_response)


def main():
    # DialoGPT-medium-joshua is my model name
    client = MyClient('DialoGPT-medium-shang-chi')

    keep_alive()
    client.run(os.environ['DISCORD_TOKEN'])

if __name__ == '__main__':
  main()