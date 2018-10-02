import vk_api


class AlreadyCreatedError(Exception):
    pass


class BotAccount:

    __account__ = None

    def __init__(self):
        self._vk = None

    @staticmethod
    def get_account():
        if BotAccount.__account__ is None:
            BotAccount.__account__ = BotAccount()
        else:
            raise AlreadyCreatedError("BotAccount has been already created")
        return BotAccount.__account__

    def auth(self, login, password):
        try:
            self._vk = vk_api.VkApi(login, password)
            self._vk.auth()
        except vk_api.AuthError:
            pass

    def method(self, method, args):
        try:
            message = self._vk.method(method, args)
            return message
        except vk_api.VkApiError as error:
            print(error)
