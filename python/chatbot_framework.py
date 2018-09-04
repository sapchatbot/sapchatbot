###
# Required Imports
###
import http.server
import json
import asyncio
from botbuilder.schema import (Activity, ActivityTypes, ChannelAccount)
from botframework.connector import ConnectorClient
from botframework.connector.auth import (MicrosoftAppCredentials,
                                         JwtTokenValidation, SimpleCredentialProvider)
import chatbot_core

####
# Credentials from the Application Registration Portal
# Maintain in : https:// apps.dev.microsoft.com
# Copy the Application ID
# Copy the password (will be displayed only once)
####
APP_ID = '5ce4d62d-4611-4fc0-8725-4db8b943580e'
APP_PASSWORD = 'lnadRVAYKR3887?dieN8+(:'
WELCOME_MSG = 'Welcome to the SAP Chatbot!'


####
# Any action with the bot will be redirected to the Handler
# Appropriate Methods are incorporated to handle the events
###
class ChatbotHandler(http.server.BaseHTTPRequestHandler):

    # Creating a reply message
    @staticmethod
    def __create_reply_activity(request_activity, text):
        """
        Post a reply to the message
        :param request_activity: Activity forwarded from Handler
        :param text: Message
        :return: Reply Activity to be posted
        """
        return Activity(
            type=ActivityTypes.message,
            channel_id=request_activity.channel_id,
            conversation=request_activity.conversation,
            recipient=request_activity.from_property,
            from_property=request_activity.recipient,
            text=text,
            service_url=request_activity.service_url)

    # As soon as interaction with the Bot begins - method is triggered
    def __handle_conversation_update_activity(self, activity):
        """
        Handle any conversation update (triggers when bot is added)
        :param activity:
        :return:
        """
        self.send_response(202)
        self.end_headers()
        if activity.members_added[0].id != activity.recipient.id:
            # if any member is added
            credentials = MicrosoftAppCredentials(APP_ID, APP_PASSWORD)
            # reply with Welcome Message
            reply = ChatbotHandler.__create_reply_activity(activity, WELCOME_MSG)
            connector = ConnectorClient(credentials, base_url=reply.service_url)
            connector.conversations.send_to_conversation(reply.conversation.id, reply)

    # Any message pinged to the bot is handled here
    def __handle_message_activity(self, activity:Activity):
        self.send_response(200)
        self.end_headers()
        credentials = MicrosoftAppCredentials(APP_ID, APP_PASSWORD)

        connector = ConnectorClient(credentials, base_url=activity.service_url)
        print('User says %s' % activity.text)

        activity.text = filterUserMention(activity.text)  # def : group chat fix
        resp_text = chatbot_core.df_query(activity.text) #process query to dialog flow

        if resp_text is None:
            resp_text = 'There is no response from the Bot.'

        reply = ChatbotHandler.__create_reply_activity(activity, resp_text)
        # reply = BotRequestHandler.__create_reply_activity(activity, 'You said: %s' % activity.text)
        connector.conversations.send_to_conversation(reply.conversation.id, reply)
        print(activity)

    def __handle_authentication(self, activity):
        credential_provider = SimpleCredentialProvider(APP_ID, APP_PASSWORD)
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(JwtTokenValidation.authenticate_request(
                activity, self.headers.get("Authorization"), credential_provider))
            return True
        except Exception as ex:
            self.send_response(401, ex)
            self.end_headers()
            return False
        finally:
            loop.close()

    def __unhandled_activity(self):
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        data = json.loads(str(body, 'utf-8'))
        activity = Activity.deserialize(data)

        if not self.__handle_authentication(activity):
            return

        if activity.type == ActivityTypes.conversation_update.value:
            self.__handle_conversation_update_activity(activity)
        elif activity.type == ActivityTypes.message.value:
            self.__handle_message_activity(activity)
        else:
            self.__unhandled_activity()

####
# During group conversation : '@sapchatbot message' returns as
# <at>SAP CHATBOT</at> [message] - input
# This function splits the username and message and gives out [message]
####
def filterUserMention(text):
    out = text
    if "<at>" in text:
        out = text.split("</at>")[-1].strip()
    return out