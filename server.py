import socket
import threading
import sys
from _thread import *
import time

class Servidor():
	def __init__(self):

		self.clients = [];
		self.nicknames = [];
		self.ip_clients = [];
		self.port_clients = [];
		self.whispers = [];

	def msg_to_all(self, msg, client):
		for c in self.clients:
			try:
				if c != client and self.whispers[self.clients.index(c)] == -1:
					c.send(msg);
			except:
				self.clients.remove(c);

# define host and port
host = '';
port = 8888;
a = '';

# create the socket
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
	print("Connection failed")
	sys.exit();

print("Socket Created!")

# bind the socket to the host and port previously specified
try:
	s.bind((host, port))
except socket.error:
	print("Binding failed")
	sys.exit();

print("Socket has been bounded!")

# server is listening for connections
s.listen(10)

print("Server is ready!\n")

serv = Servidor()

# thread for accept connections
def acceptCon(a):
	while True:
		try:
			conn, addr = s.accept();
			start_new_thread(clientThread, (conn, addr,));
		except:
			print("error!")
			sys.exit();

# thread for connection with client
def clientThread(conn, addr):
	# Client is choosing a username...
	conn.send("nickname".encode());
	nickname = conn.recv(1024).decode();
	check = False;
	
	while(True):
		check = False;
		for n in serv.nicknames:
			if nickname == n:
				check = True;
				break;

		if check == False:
			conn.send("Nickname accepted".encode());
			break;
		else:
			conn.send("nickname2".encode());
			nickname = conn.recv(1024).decode();


	print(nickname + " has connected!");
	serv.clients.append(conn);
	serv.nicknames.append(nickname);
	serv.ip_clients.append(addr[0]);
	serv.port_clients.append(addr[1]);
	serv.whispers.append(-1);

	time.sleep(.25);
	# Greetings!
	welcomeMessage = "Welcome to the chat " + nickname + "!\n" + "Type commands() to see a list of commands!\n" + "Type something and hit Enter to send!\n";
	conn.send(welcomeMessage.encode())

	print("LIJSKOENGIOUAJSDHNBGASDE");
	# Tell the others!
	serv.msg_to_all((nickname + " entered the chat!\n").encode(), conn);

	# Processing messages coming from the client...
	while True:
		data = conn.recv(1024);
		if not data:
			break;
		reply = data.decode();
		myIndex = serv.clients.index(conn);
		
		# If the client wants to see the list of commands...
		if reply == "commands()":
			listOfCommands = "list() - show the list of clients using the chat\n" + "private(*) - starts a private chat with user *\n" + "quit() - exits the private chat and returns to global chat\n" + "nickname(*) - change current nickname to *\n" + "exit() - exits the chat\n";
			conn.send(listOfCommands.encode());

		# If the client wants to see the list of users...
		elif reply == "list()":
			listString = "";
			for (n,i,p) in zip(serv.nicknames, serv.ip_clients, serv.port_clients):
				if serv.whispers[serv.nicknames.index(n)] == -1:
					listString = listString + "Nickname: " + n + "  IP: " + str(i) + "  Port: " + str(p) + "\n";
				else:
					listString = listString + "Nickname: " + n + " (privado)" + "  IP: " + str(i) + "  Port: " + str(p) + "\n";
			conn.send(listString.encode());

		#Answer to private chat
		elif(reply == "y" or reply == "n"):
			#resend msg
			conn.send(("*pvt*" + reply).encode());

		# If the client wants to whisper to someone...
		elif reply[:8] == "private(" and reply[-1:] == ")":
			# If he typed a valid nickname, invites the other client to private chat
			if reply[8:-1] in serv.nicknames and reply[8:-1] != nickname:
				wIDd = serv.nicknames.index(reply[8:-1]);
				wInvite = nickname + " wants to private chat with you. Do you accept it? y-yes / n-no";
				conn.send(("waiting for " + reply[8:-1] + " response...\n").encode());
				serv.clients[wIDd].send(wInvite.encode());
				wAnswer = serv.clients[wIDd].recv(1024).decode();
				# If the other client accepted, start the private chat
				if wAnswer == "y":
					serv.whispers[myIndex] = wIDd;
					serv.whispers[wIDd] = myIndex;
					conn.send(("whisper" + serv.nicknames[wIDd]).encode());
					serv.clients[wIDd].send(("whisper" + nickname).encode());
				# Otherwise, send to the first client a sad message :(
				else:
					wMessage = reply[8:-1] + " didnt accept to private chat with you. A real punch in the face! e.e\n";
					conn.send(wMessage.encode())
			# Otherwise, send a error message!
			else:
				wMessage = "user " + reply[8:-1] + " is invalid!\n";
				conn.send(wMessage.encode());

		# If the client wants to quit the private chat...
		elif reply == "quit()":
			# If the client isnt in a private chat, send a error message to him
			if serv.whispers[myIndex] == -1:
				conn.send("You arent in a private chat!\n".encode());
			# Otherwise, terminate the private chat and make both clients return to global chat
			else:
				serv.clients[serv.whispers[myIndex]].send("Private chat terminated. You've returned to the global chat!\n".encode());
				conn.send("Private chat terminated. You've returned to the global chat!\n".encode());
				serv.whispers[serv.whispers[myIndex]] = -1;
				serv.whispers[myIndex] = -1;

		#If the client wants to change nickname...
		elif (reply[:9] == "nickname(" and reply[-1:] == ")"):
			newNick = reply[9:-1];
			check = False;

			#Check if new nick is already in use
			for (n) in serv.nicknames:
				if n == newNick:
					check = True;
					break;
			if check == True:
				conn.send("Nickname is already in use".encode());

			else:
				serv.nicknames[myIndex] = newNick;
				nickname_message = nickname + " changed nickname to " + newNick + "\n";
				print(nickname + " changed nickname to " + newNick);
				serv.msg_to_all(nickname_message.encode(), conn);
				nickname = newNick;

		# If the client wants to quit the chat...
		elif reply == "exit()":
			# If the client was in a private chat with someone, terminates the private chat and makes that someone returns to global chat
			if serv.whispers[myIndex] != -1:
				serv.clients[serv.whispers[myIndex]].send((nickname + " has left the chat. Youre returning to the global chat...\n").encode());
				serv.whispers[serv.whispers[myIndex]] = -1;
			# Delete all information about the client
			serv.nicknames.pop(myIndex);
			serv.ip_clients.pop(myIndex);
			serv.port_clients.pop(myIndex);
			serv.clients.pop(myIndex);
			serv.whispers.pop(myIndex);
			serv.msg_to_all((nickname + " left the chat!\n").encode(), conn);
			print(nickname + " left the chat!");
			break;

		# If the client wants to send a message...
		else:
			reply = nickname + " sent: " + reply;
			# If he is private chating with someone, only sends the message to that person
			if serv.whispers[myIndex] == -1:
				print(reply);
				serv.msg_to_all(reply.encode(), conn);
			# Otherwise, he is in global chat -> send the message to everyone
			else:
				serv.clients[serv.whispers[myIndex]].send(reply.encode());

start_new_thread(acceptCon, (a,));

# server is always accepting connections and creating threads for each connection
while True:
		msg = input()
		if msg == 'exit()':
			for c in serv.clients:
				c.send("kill".encode());
			s.close();
			sys.exit();
			pass;
		elif msg == "list()":
			if(len(serv.clients) != 0):
				for (n,i,p) in zip(serv.nicknames, serv.ip_clients, serv.port_clients):
					if serv.whispers[serv.nicknames.index(n)] == -1:
						print("Nickname: " + n + "  IP: " + str(i) + "  Port: " + str(p));
					else:
						print("Nickname: " + n + " (privado)" + "  IP: " + str(i) + "  Port: " + str(p));
			else:
				print("There is no one here!");
