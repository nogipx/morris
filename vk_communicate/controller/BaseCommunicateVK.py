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
    def create_session(token=None, login=None, password=None, api_v='5.85'):
        try:
            if token:
                session = vk_api.VkApi(token=token, api_version=api_v)

            elif login and password:
                session = vk_api.VkApi(login, password, api_version=api_v)

            else:
                raise vk_api.AuthError("Define login and password or token.")

            return session

        except vk_api.ApiError as error:
            logging.info(error)

    def get_last_message(self, user_id):

        return self.api.messages.getHistory(
            peer_id=user_id, count=1)["items"][0]

    @staticmethod
    def get_attachments(last_message):

        if not last_message or "attachments" not in last_message:
            return ""

        attachments = last_message["attachments"]
        attach_strings = []

        for attach in attachments:

            attach_type = attach["type"]
            attach_info = attach[attach_type]

            attach_id = attach_info["id"]
            attach_owner_id = attach_info["owner_id"]

            if "access_key" in attach_info:
                access_key = attach_info["access_key"]
                attach_string = "{}{}_{}_{}".format(attach_type, attach_owner_id, attach_id, access_key)

            else:
                attach_string = "{}{}_{}".format(attach_type, attach_owner_id, attach_id)

            attach_strings.append(attach_string)

        return ",".join(attach_strings)

    @staticmethod
    def get_forwards(attachments, last_message):

        if not attachments or "fwd_count" not in attachments:
            return ""

        if len(last_message["fwd_messages"]) == int(attachments["fwd_count"]):
            return last_message["id"]

    def send(self, user_id, message, attachments=None, destroy=False, destroy_type=0, **kwargs):
        send_to = int(user_id)

        if "last_message" in kwargs:
            last_message = kwargs["last_message"]
        else:
            last_message = None

        p_attachments = self.get_attachments(last_message)
        p_forward = self.get_forwards(attachments, last_message)

        if message or p_attachments or p_forward:
            self.api.messages.send(
                user_id=send_to, message=message,
                attachment=p_attachments,
                forward_messages=p_forward)

        if destroy:
            accept_msg_id = self.api.messages \
                .getHistory(peer_id=user_id, count=1) \
                .get('items')[0].get('id')

            self.delete(accept_msg_id, destroy_type=destroy_type)

    def delete(self, msg_id, destroy_type=1):
        self.api.messages.delete(message_id=msg_id, delete_for_all=destroy_type)