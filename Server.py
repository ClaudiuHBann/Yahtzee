# Librarii importate
import socket
import random
from collections import Counter
from typing import NamedTuple

# Variabile globale
commands = ("START", "ARUNCA", "KEEP", "PUNCTAJ",
            "ABANDON")  # Un tuple cu comenzile jocului
commandsScoreTable = [["N1", -1], ["N2", -1], ["N3", -1], ["N4", -1], ["N5", -1], ["N6", -1], ["BONUS", -1], ["JOKER", -1], ["TRIPLA", -1], [
    "CHINTA", -1], ["FULL", -1], ["CAREU", -1], ["YAMS", -1], ["TOTAL", -1]]  # Comenzile pentru tabla de scor si bonus cu total

# Functie care verifica daca tot ce e in lista1 se afla in lista 2


def L1InL2(l1, l2):
    counter1 = Counter(l1)
    counter2 = Counter(l2)
    counter1KeysList = list(counter1.keys())
    counter2KeysList = list(counter2.keys())

    for i in range(len(counter1KeysList)):
        if counter1KeysList[i] not in counter2KeysList or counter1[counter1KeysList[i]] > counter2[counter1KeysList[i]]:
            return False

    return True

# Functie pentru generarea aleatorie de numere sortate intr-o lista


def RandomInRangeSortedList(numberOfElements=5, rangeLower=1, rangeUpper=6):
    listOfOrderedRandomNumbers = []

    for _ in range(numberOfElements):
        listOfOrderedRandomNumbers.append(
            random.randint(rangeLower, rangeUpper))

    listOfOrderedRandomNumbers.sort()

    return listOfOrderedRandomNumbers

# Clasa pentru pachetele care se vor trimite la client


class PackageServer(NamedTuple):
    statusMessage: str
    object: list

# Clasa pentru pachetele care se vor primi de la client


class PackageClient(NamedTuple):
    command: str
    object: list

# Clasa pentru server, creaza un socket tcp automat si accepta clienti, suport pentru trimiterea si primirea pachetelor de date


class ServerTCP:
    # Constructor care creaza un socket tcp care poate accepta deja clienti (creaza socket, il leage de un port si incepe sa asculte)
    def __init__(self, port, ipAddress="") -> None:
        try:
            self.serverSocket = socket.socket()
            self.serverSocket.bind((ipAddress, port))
            self.serverSocket.listen()
        except socket.error as e:
            print("Error: " + str(e))

    # Metoda care trimite date catre un socket
    # Intoarce numarul de octeti trimisi catre client, altfel None
    def DataSend(self, clientSocket, data):
        try:
            return clientSocket.send(str(data).encode())
        except socket.error as e:
            print("Error: " + str(e))
            return None

    # Metoda care primeste date, mai exact packetSize octeti de la un socket
    # Intoarce un obiect cu cu date de la client, altfel None
    def DataReceive(self, clientSocket, packetSize=256):
        try:
            return eval(clientSocket.recv(packetSize).decode())
        except (socket.error, SyntaxError) as e:
            print("Error: " + str(e))
            return None

    # Metoda care accepta un socket care incearca sa se conecteze la server
    # Intoarce un tuple cu clientul conectat, altfel None
    def Accept(self):
        try:
            return self.serverSocket.accept()
        except socket.error as e:
            print("Error: " + str(e))
            return None

# Clasa pentru logica jocului yathzee pe buget


class Yams:
    # Constructor pentru initializarea datelor ca de ex
    def __init__(self, serverTCP) -> None:
        self.serverTCP = serverTCP

        self.package = None
        self.clientSocket = None
        self.dices = None
        self.rerolls = -1

    # Metoda care preaia pachetul de la client si alege ce sa se intample in functie de datele primite
    def CommandParser(self, package):
        self.package = package

        if self.package[0] == commands[3]:
            return self.SendScoreTable()

        if not self.IsCommandValid():
            return self.SendErrorMessage()

        if package[0] == commands[0] or package[0] == commands[3]:
            return self.SendScoreTable()
        elif package[0] == commands[1] or package[0] == commands[2]:
            return self.Roll()
        elif package[0] == commands[4]:
            return None
        elif [item for item in commandsScoreTable if item[0] == package[0]]:
            return self.CommandScoreTable()

    # Metoda pentru generarea de zaruri pt "ARUNCA" sau "KEEP"
    def Roll(self):
        self.rerolls += 1

        if self.rerolls > 2:
            return self.SendErrorMessage()

        if self.package[1] == None:
            self.dices = RandomInRangeSortedList()
        else:
            if not L1InL2(self.package[1], self.dices):
                self.rerolls -= 1
                return self.SendErrorMessage()

            self.dices = self.package[1] + \
                RandomInRangeSortedList(5 - len(self.package[1]))
            self.dices.sort()

        return self.SendDices()

    # Metoda pentru verificarea comenzilor primite daca sunt bune
    def IsCommandValid(self) -> bool:
        if self.package[0] in commands:
            return True

        for i in range(0, len(commandsScoreTable)):
            if self.package[0] == commandsScoreTable[i][0]:
                return True

        return False

    # Metoda pentru comenzile tabelei de scoruri
    def CommandScoreTable(self):
        indexScoreTable = 0

        for i in range(0, len(commandsScoreTable)):
            if commandsScoreTable[i][0] == self.package[0]:
                indexScoreTable = i
                break

        if indexScoreTable == 6 or indexScoreTable == 13 or commandsScoreTable[indexScoreTable][1] != -1:
            return self.SendErrorMessage()

        counterDict = dict(Counter(self.dices))
        counterDictValuesSorted = list(counterDict.values())
        counterDictValuesSorted.sort(reverse=True)

        if indexScoreTable == 0 and 1 in counterDict:
            commandsScoreTable[0][1] = counterDict[1]
        elif indexScoreTable == 1 and 2 in counterDict:
            commandsScoreTable[1][1] = counterDict[2] * 2
        elif indexScoreTable == 2 and 3 in counterDict:
            commandsScoreTable[2][1] = counterDict[3] * 3
        elif indexScoreTable == 3 and 4 in counterDict:
            commandsScoreTable[3][1] = counterDict[4] * 4
        elif indexScoreTable == 4 and 5 in counterDict:
            commandsScoreTable[4][1] = counterDict[5] * 5
        elif indexScoreTable == 5 and 6 in counterDict:
            commandsScoreTable[5][1] = counterDict[6] * 6
        elif indexScoreTable == 7:
            commandsScoreTable[7][1] = sum(self.dices)
        elif indexScoreTable == 8 and counterDictValuesSorted[0] >= 3:
            commandsScoreTable[8][1] = sum(self.dices)
        elif indexScoreTable == 9 and sorted(self.dices) == list(range(min(self.dices), max(self.dices) + 1)):
            commandsScoreTable[9][1] = 20
        elif indexScoreTable == 10 and counterDictValuesSorted[0] == 3 and counterDictValuesSorted[1] == 2:
            commandsScoreTable[10][1] = 30
        elif indexScoreTable == 11 and counterDictValuesSorted[0] >= 4:
            commandsScoreTable[11][1] = 40
        elif indexScoreTable == 12 and counterDictValuesSorted[0] == 5:
            commandsScoreTable[12][1] = 50
        else:
            commandsScoreTable[indexScoreTable][1] = 0

        sumOfNs = 0
        for i in range(0, 6):
            if commandsScoreTable[i][1] != -1:
                sumOfNs += commandsScoreTable[i][1]

        if sumOfNs >= 63:
            commandsScoreTable[6][1] = 50
        else:
            commandsScoreTable[6][1] = 0

        sumTotal = sumOfNs
        for i in range(6, len(commandsScoreTable) - 1):
            if commandsScoreTable[i][1] != -1:
                sumTotal += commandsScoreTable[i][1]

        commandsScoreTable[len(commandsScoreTable) - 1][1] = sumTotal

        allAreFull = True
        for i in range(0, len(commandsScoreTable) - 1):
            if i != 6 and commandsScoreTable[i][1] == -1:
                allAreFull = False

        if allAreFull:
            self.SendScoreTable()
            return None

        self.rerolls = -1
        return self.SendScoreTable()

    # Wrapper pentru trimiterea unui pachet cu tabla de scor
    def SendDices(self):
        return self.serverTCP.DataSend(self.clientSocket[0], PackageServer(None, self.dices))

    # Wrapper pentru trimiterea unui pachet cu tabla de scor
    def SendScoreTable(self):
        return self.serverTCP.DataSend(self.clientSocket[0], PackageServer(None, commandsScoreTable))

    # Wrapper pentru trimiterea unui pachet cu eroare
    def SendErrorMessage(self):
        return self.serverTCP.DataSend(self.clientSocket[0], PackageServer("COMANDA ERONATA", None))

    # Metoda pentru resetarea variabilelor unui client
    def ResetVars(self) -> None:
        self.clientSocket = None
        self.package = None
        self.dices = None
        self.rerolls = -1

        for i in range(0, len(commandsScoreTable)):
            commandsScoreTable[i][1] = -1

    # Metoda pentru logica jocului yams high level adica resetam variabilele acceptam un client si il luam mesaje pe care le trimitem la parser-ul de comenzi
    def Loop(self):
        while True:
            self.ResetVars()
            self.clientSocket = self.serverTCP.Accept()

            while True:
                receivedData = self.serverTCP.DataReceive(self.clientSocket[0])
                if receivedData == None or self.CommandParser(receivedData) == None:
                    break


# Cream un obiect yams cu un parametru server si apelam o metoda de la yams in care avem logica high level
Yams(ServerTCP(13000)).Loop()
