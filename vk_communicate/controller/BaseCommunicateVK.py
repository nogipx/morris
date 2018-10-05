from vk_api.longpoll import VkLongPoll

import vk_api
import logging


class BaseCommunicateVK:

    longpoll = None

    def __init__(self, vksession):
        self.session = vksession
        self.api = vksession.get_api()
        if BaseCommunicateVK.longpoll is None:
            BaseCommunicateVK.longpoll = VkLongPoll(self.session)

    def get_api(self):
        return self.api

    def get_longpoll(self):
        return self.longpoll

    def method(self, func, args):
        return self.api.method(func, args)
    
    @staticmethod
    def create_session(token=None, login=None, password=None):
        try:
            if token:
                session = vk_api.VkApi(token=token)

            elif login and password:
                session = vk_api.VkApi(login, password)

            else:
                raise vk_api.AuthError("Define login and password or token.")

            return session

        except vk_api.ApiError as error:
            logging.info(error)

    @staticmethod
    def parse_attachments(attachments):

        if not attachments:
            return ""

        attach = []
        result = ""
        files = attachments
        amount = 1

        for file in files.keys():

            if str(file).endswith('type'):
                attach.append((files.get('attach{0}_type'.format(amount)) + files.get('attach{0}'.format(amount))))
                amount += 1

        for i in attach:
            result += '{},'.format(i)

        return result

    def get_forwards(self, forward, user_id):

        if forward is None or not "fwd_count" in forward:
            return ""

        last_msg = self.api.messages.getHistory(user_id=user_id, count=1)["items"][0]

        if len(last_msg["fwd_messages"]) == int(forward["fwd_count"]):
            return last_msg["id"]

        else:
            self.api.send(user_id, "Slowly, dude. Plz.")
            return ""

    def send(self, user_id, message, attachments=None, destroy=False, destroy_type=0):
        send_to = int(user_id)
        status = True

        if message or attachments:
            try:
                self.api.messages.send(
                    user_id=send_to,
                    message=message,
                    attachment=self.parse_attachments(attachments),
                    forward_messages=self.get_forwards(attachments, user_id))

            except Exception as err:
                logging.error(err)
                status = False
        else:
            logging.error('There are not message and attachment.')

        if destroy:
            accept_msg_id = self.api.messages.getHistory(peer_id=user_id, count=1)\
                .get('items')[0].get('id')

            self.delete(accept_msg_id, destroy_type=destroy_type)

        return status

    def delete(self, msg_id, destroy_type=1):
        self.api.messages.delete(message_id=msg_id, delete_for_all=destroy_type)