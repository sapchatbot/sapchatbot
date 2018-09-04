# Required Imports
import http.server
import os
import chatbot_framework

port = int(os.getenv("PORT", 9009))

try:
    SERVER = http.server.HTTPServer(('0.0.0.0', port),
                                    chatbot_framework.ChatbotHandler)
    print('Started SAP Chatbot Server...')
    SERVER.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down server')
    SERVER.socket.close()
