import socket
from collections import Counter
from typing import NamedTuple

commands = ("START", "ARUNCA", "KEEP", "PUNCTAJ", "ABANDON")

# Clasa pentru pachetele care se vor trimite la client


class PackageServer(NamedTuple):
    statusMessage: str
    object: list

# Clasa pentru pachetele care se vor timite la server


class PackageClient(NamedTuple):
    command: str
    object: list

# Clasa pentru client-ul tcp pentru conectarea la server, trimiterea sau primirea datelor


class ClientTCP:
    # Constructor pentru crearea unui socket tcp si conectarea la un server
    def __init__(self, serverIP, serverPort) -> None:
        try:
            self.clientSocket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.clientSocket.connect((serverIP, serverPort))
        except socket.error as e:
            print("Error: " + str(e))

    # Metoda pentru trimiterea de date la server
    def DataSend(self, data):
        try:
            return self.clientSocket.send(str(data).encode())
        except socket.error as e:
            print("Error: " + str(e))
            return None

    # Metoda pentru primirea datelor de la server
    def DataReceive(self, packetSize=256):
        try:
            return eval(self.clientSocket.recv(packetSize).decode())
        except socket.error as e:
            print("Error: " + str(e))
            return None

# Clasa pentru logica jocului yams in client


class Yams:
    # Constructor in care pasam clientul tcp si trimitem comanda "START" si "ARUNCA"
    def __init__(self, clientTCP) -> None:
        self.clientTCP = clientTCP
        self.package = None

        self.clientTCP.DataSend(PackageClient(commands[0], None))
        self.GetTable()

        self.clientTCP.DataSend(PackageClient(commands[1], None))
        self.GetDices()

    # Metoda pentru afisarea tabelei de scor
    def PrintTable(self):
        for (first, second) in self.package[1]:
            first += ' '

            while len(first) < 8:
                first += '-'

            first += '>'

            if second != -1:
                print(first + ' ' + str(second))
            else:
                print(first)

        print()

    # Metoda pentru afisarea zarurilor
    def PrintDices(self):
        print(str(self.package[1]) + " R = " +
              str(max([item[1] for item in list(Counter(self.package[1]).items())])), end="\n\n")

    # Metoda pentru primirea tablei de scor si afisarea acesteia
    def GetTable(self):
        self.package = self.clientTCP.DataReceive()

        if self.package[1] == None:
            print(self.package[0])
        else:
            self.PrintTable()

    # Metoda pentru primirea zarurilor si afisarea acestora
    def GetDices(self):
        self.package = self.clientTCP.DataReceive()

        if self.package[1] == None:
            print(self.package[0])
        else:
            self.PrintDices()

    # Metoda ce contine logica jocului
    def Loop(self):
        while True:
            command = input().upper()
            print()
            commandSplit = command.split()

            if commandSplit[0] == commands[4]:
                break

            self.package = PackageClient(commandSplit[0], [int(s) for s in commandSplit if s.isdigit()]) if len(
                commandSplit) > 1 else PackageClient(commandSplit[0], None)

            self.clientTCP.DataSend(self.package)
            self.package = self.clientTCP.DataReceive()

            if self.package[1] == None:
                print(self.package[0], end="\n\n")
            else:
                if all(isinstance(item, int) for item in self.package[1]):
                    self.PrintDices()
                else:
                    self.PrintTable()

                    if commandSplit[0] == commands[3]:
                        continue

                    self.clientTCP.DataSend(PackageClient(commands[1], None))
                    self.package = self.clientTCP.DataReceive()

                    if self.package == None:
                        break

                    self.PrintDices()


# Cream un obiect yams si ii pasam un client tcp si apelam metoda loop
Yams(ClientTCP("127.0.0.1", 13000)).Loop()
