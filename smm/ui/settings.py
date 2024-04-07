from kivy.event import EventDispatcher
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore


class Settings(EventDispatcher):
    openapi_token = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = JsonStore('settings.json')

        self._read_settings()

    def _read_settings(self):
        if 'openapi_token' in self.store:
            self.openapi_token = self.store.get('openapi_token')['value']

    def on_openapi_token(self, openapi_token):
        self.store.put('openapi_token', value=openapi_token)
