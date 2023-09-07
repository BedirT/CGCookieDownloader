import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DownloadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    # You can use this method to send updates to the client
    async def send_update(self, message):
        await self.send(text_data=json.dumps(message))
