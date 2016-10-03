#-*- coding = utf-8 -*-
import tornado.web
import json
from tornado import websocket

# General modules.
import logging

"""
    Django send messages to all the others
    A client has a WebSocketConection with this process
    This connection has to be authorised -> Token/other : how to check that the user is authorised ? ChatHandler has a list of authorized tokens
    Connections only accept messages from Django
    
    Proccess : 
        - User logs in -> Django send token to MainHandler
        - User sent message -> Django save it and give it to the MainHandler, which gives it to the appropriated connections -> clients
        - User logs out -> Django tell MainHandler to remove the token from the list
"""
class MainHandler(tornado.web.RequestHandler):

    def initialize(self, chat_handler):
        """Store a reference to the "external" ChatHandler instance"""
        self.__ch = chat_handler

    def _get_current_user(self, param, callback):
        """
        Check if the message really originates from Django.
        """
        try:
            secret = self.get_query_argument("secret_key")
            if(secret == ""):
                #add user to the chat he is member of
                self._current_user = "Django"
                print("Right user.")
                print(self.request)
                print(self.request.arguments)
                print(self.get_argument("message", strip=False))
                param = json.loads(self.get_argument("message", strip=False))
                print(param)
                callback(param)
                print("Callback called.")
                self.set_status(200, "All right")
                print("get current user finished")
                return
            else:
                print("request not from Django")
                self._current_user = None
                self.set_status(403, "You are not authorised to access this server.")
                self.finish()
        except tornado.web.MissingArgumentError:
            print("request not from Django")
            self._current_user = None
            self.set_status(403, "You are not authorised to access this server.")
            self.finish()

    def get(self, token=None):
        """
            Add a client to the list of authorized ones
        """
        if not token:
            self.set_status(403, "You are not authorised to access this server.")
        # Get the current user.
        self._get_current_user(param=token, callback=self.__ch.add_potential_client)
        print("get finish.")

    def post(self, message=None):
        """
            Post a message from Django
        """
        print("Get method called")
        if not message:
            self.set_status(400, "Bad Request.")
            self.finish()
        print("Get Method successfully called")
        # Get the current user.
        self._get_current_user(param=message, callback=self.__ch.add_message)
        print("post finish.")
        self.set_status(200, "All right")
        print("post not finished yet")
        return

    def delete(self, token=None):
        """
            Remove a client from the list of authorized ones
        """
        if not token:
            self.set_status(403, "You are not authorised to access this server.")
            self.finish()
        # Get the current user.
        self._get_current_user(param=token, callback=self.__ch.remove_potential_client)
        self.finish()


class ClientWSConnection(websocket.WebSocketHandler):
 
    def initialize(self, chat_handler):
        """Store a reference to the "external" ChatHandler instance"""
        self.__ch = chat_handler
 
    def open(self, token):
        for user in self.__ch.authorized_tokens:
            if user.token == token.token and user.user.id == token.user_id:
                self.__ch.add_client_wsconn(user, self)
                print("WebSocket opened. ClientID = %s" % self.__token.user_id)
                break
        self.close(reason="You are not allowed to establish a connection with this server.", code=403)
 
    def on_message(self, message):
        print("Try to send a message the wrong way.")
 
    def on_close(self):
        print("WebSocket closed")
        self.__ch.remove_client(self.__token.user_id)

"""
    Needs:
        - authorized_tokens = [{'token': token, 'user': user}]
        - add_potential_client({'token': token, 'user': user})
        - add_client_wsconn(user, ClientWSConnection)
        - remove_client(user_id)
        - remove_potential_client({'token': token, 'user': user})
        - add_message(message)
        - chatemate_cwsconns(user_id)
        - send_is_connected_msg(user_id)
        - send_is_disconnected_msg(user_id)
"""
class ChatHandler(object):
    """Store data about connections, chats, which users are in which chats, etc."""
 
    def __init__(self):
        self.authorized_tokens = []  # store the list of {'token': token, 'user': user}
        self.user_connections = {} # dict  to store 'user_id': {'wsconn": wsconn, 'chats': [chat_id1, chat_id2]}
        self.chatmates = {}  # store a set for each chat, each contains the id of the clients in the room.
 
    def add_potential_client(self, token):
        """Add potential client to chat."""
        self.authorized_tokens.append(token)
 
    def add_client_wsconn(self, user, conn):
        """Store the websocket connection corresponding to an authorized client."""
        self.user_connections[user.id]['wsconn'] = conn
        self.user_connections[user.id]['chats'] = []
 
        # for each chat this user is member of, add the user to the chatmates of the chat
        for chatmember in user.user_chatmember:
            self.chatmates[chatmember.chat.id].add(user.id)
            self.user_connections[user.id]['chats'].append(chatmember.chat.id)

        # send "is_connected" messages
        self.send_is_connected_msg(user.id)
 
    def remove_client(self, user_id):
        """Remove all client information from the chat handler."""
        # first, remove the client connection from the corresponding chat in self.chatmates
        chats = self.user_connections[user_id]
        self.send_is_disconnected_msg(user_id)
        for chat_id in chats:
            self.chatmates[chat_id].discard(user_id)
        del self.user_connections[user_id]
 
    def remove_potential_client(self, token):
        """Remove potential client from chat."""
        del self.authorized_tokens[token]
        remove_client(token.user.id)

    def add_message(self, message):
        print('begin of the add_message method')
        print(message)
        print(message['chat'])
        print(message['chat']['id'])
        rconns = self.chatmate_cwsconns(message['chat']['id'])
        print(rconns)
        for conn in rconns:
            conn.write_message(message)
            print("Message sent")
        print("end of the sent messages");
 
    def chatmate_cwsconns(self, chat_id):
        """Return a list with the connections of the users currently connected to the specified chat."""
        print('begin of the chatmate_cwsconns method.')
        print(self.chatmates)
        if chat_id in self.chatmates:
            print("found")
            return self.chatmates[chat_id]
        else:
            print('not found')
            return []
 
    def send_is_connected_msg(self, user_id):
        """Send a message of type 'is_connected' to all users connected to the chat where user_id is connected."""
        r = set()
        #for every chat the user is part of
        for chat in self.user_connections[user_id]['chats']:
            #add the other members of the chat to the list of receivers
            r.update(self.chatmate_cwsconns(chat))
        msg = {"msgtype": "is_connected", "username": user_id}
        pmessage = json.dumps(msg)
        for conn in r_cwsconns:
            conn.write_message(pmessage)
 
    def send_is_disconnected_msg(self, user_id):
        """Send a message of type 'is_disconnected' to all users connected to the chat where user_id is disconnected."""
        r = set()
        #for every chat the user is part of
        for chat in self.user_connections[user_id]['chats']:
            #add the other members of the chat to the list of receivers
            r.update(self.chatmate_cwsconns(chat))
        msg = {"msgtype": "is_disconnected", "username": user_id}
        pmessage = json.dumps(msg)
        for conn in r_cwsconns:
            conn.write_message(pmessage)
