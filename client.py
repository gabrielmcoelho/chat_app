import socket
import threading
import sys

class Client():
	

	def __init__(self, host="localhost", port=8888):
		
		# Initializing client socket and properties
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		self.sock.connect((host, port));
		self.whispering = 0;
		self.wNickname = "";
		self.kill = 0;

		# Defining client's username
		data = self.sock.recv(1024);
		while(data.decode() != "nickname"):
			pass
		nick = input('Choose a nickname to begin the chat: ');
		self.sock.send(nick.encode());
		confirmMSG = self.sock.recv(1024).decode();
		while(confirmMSG == "nickname2"):
			nick = input("Nickname is already in use. Please choose another nickname: ");
			self.sock.send(nick.encode());
			confirmMSG = self.sock.recv(1024).decode();

		# Initializing thread that reads messages
		read_msg = threading.Thread(target=self.read_msg);
		read_msg.daemon = True;
		read_msg.start();

		# Client's input loop
		while True:
			msg = input();
			if self.kill == 0:
				self.send_msg(msg);
			else:
				self.sock.close();
				sys.exit();

	# Function to send messages
	def send_msg(self, msg): 
		self.sock.send(msg.encode());
		if msg=="exit()":
			print("Bye Bye. See you later!");
			self.sock.close();
			sys.exit();
		else:
			pass;

	# Thread to read messages
	def read_msg(self):
		while True:
			try:
				data = self.sock.recv(1024);
				if data:
					rmsg = data.decode();
					if rmsg[:7] == "whisper":
						print("You are now in a private chat with " + rmsg[7:] + "\n");
						self.whispering = 1;
						self.wNickname = rmsg[7:];
					elif rmsg[:5] == "*pvt*":
						self.sock.send(rmsg[5:].encode())
					elif rmsg[:23] == "Private chat terminated":
						self.whispering = 0;
						self.wNickname = "";
						print(rmsg);
					elif rmsg == "kill":
						self.kill = 1;
					else:
						if self.whispering == 0:
							print(rmsg);
						elif self.whispering == 1:
							print("(pvt)" + rmsg)
			except:
				print("Client terminated due to server shutdown! Bye Bye...");
				sys.exit();

c = Client()
