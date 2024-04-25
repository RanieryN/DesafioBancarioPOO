from abc import ABC,abstractmethod
from datetime import datetime
from pathlib import Path
import os

ROOT_PATH = Path(__file__).parent
 
# Classes

# Cliente

class ContaIterador:
    def __init__(self,contas):
        self.contas = contas
        self.contador = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            texto  = (f"{self.contas[self.contador]} {'='*100}")
            self.contador += 1
            return texto
        except IndexError:
            raise StopIteration

class Cliente:
    def __init__(self,endereco):
        self._endereco=endereco
        self.contas=[]

    def realizar_transacao(self,conta, transacao):
        if len(conta.historico.transacoes_do_dia())>= 4:
            print("Você excedeu o número de transaçoes permitidas para hoje!")
            return
        
        transacao.registrar(conta)
    
    def adicionar_conta(self,conta):
        self.contas.append(conta)

    def getContas(self):
        for conta in self.contas:
            print(f"""
                    Conta: {conta.getDados()}
            """)


class PessoaFisica(Cliente):
    def __init__(self,cpf,nome,data_nascimento,endereco):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome= nome
        self._data_nascimento = data_nascimento

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self._nome}','{self._cpf}')>"

    def getDados(self):
        return f"Nome: {self._nome} - CPF: {self._cpf} - Data Nascimento: {self._data_nascimento}"

    def __str__(self):
        return self.getDados()


# Conta e Conta Corrente
 
class Conta:
    def __init__(self,cliente,numero):
        self._saldo = 0
        self._numero = numero
        self._agencia ="0001"
        self._cliente = cliente
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls,cliente,numero):
        return cls(numero,cliente)
    
    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    

    def sacar(self,valor):
        if valor <= self._saldo:
            self._saldo = self._saldo - valor
            print("Saque realizado com sucesso !")
            response = True
        else:
            print("Erro ao tentar sacar o dinheiro! saldo insuficiente")
            response = False
        return response
    
    def depositar(self,valor):
        if valor > 0:
            self._saldo = self._saldo + valor
            print("Depositado com sucesso !")
            response = True
        else:
            print("Erro ao depositar, o valor não é valido")
            response = False
        return response
    
    def getDados(self):
        return f"""   Cliente:{self._cliente}  - Agencia:{self._agencia} Numero:{self._numero}
                     Saldo:{self._saldo} 

        """
    
    def __str__(self):
        return f""" \n Agencia: {self.agencia}
                       C/C:   {self.numero} 
                       Titular:\t{self.cliente}

                """
class ContaCorrente(Conta):
    def __init__(self,numero,cliente,limite=500,limite_saques=3):
        super().__init__(cliente, numero)
        self.limite = limite
        self.limite_saques = limite_saques
        self._saques_realizados = 0
 
    def sacar(self,valor):
        if valor <= self._saldo and valor <= self.limite and self._saques_realizados < self.limite_saques:
            super().sacar(valor)
            self._saques_realizados = self._saques_realizados + 1
            response = True
        else:
            print("Erro ao tentar sacar o dinheiro! saldo insuficiente|Limite excedido")
            response = False
        return response
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente._nome}')>"
    def depositar(self,valor):
        if valor > 0:
            super().depositar(valor)
            response = True
        else:
            print("Erro ao depositar, o valor não é valido")
            response = False
        return response
    

# Interface

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @abstractmethod
    def registrar(self,conta):
        pass

class Deposito(Transacao):
    def __init__(self,valor):
        self._valor = valor
    @property
    def valor(self):
        return self._valor
        
    def registrar(self,conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

           
class Saque(Transacao):
    def __init__(self,valor):
        self._valor = valor

    @property    
    def valor(self):
        return self._valor
    
    def registrar(self,conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

# Historico

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self,transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor":transacao.valor,
                "data": datetime.now().strftime("%d-%m-%y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self,tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao
    
    def transacoes_do_dia(self):
        data_atual = datetime.now().strftime("%d-%m-%y %H:%M:%S")
        transacoes = []

        for transacao in self._transacoes:
            data_transacao = datetime.strptime(transacao["data"], "%d-%m-%y %H:%M:%S")
            if data_atual == data_transacao:
                transacoes.append(transacao)
        return transacoes
            


# Iterador

def log_transacao(func):
    def envelope(*args,**kwargs):
        resultado = func(*args,**kwargs)
        date = datetime.now().strftime("%d-%m-%y %H:%M:%S")
        texto = f":[{date}] | Funcao: {func.__name__} | Executada com argumentos: {args} e {kwargs} Retornou: {resultado}\n"

      
        # fazer o log.txt
        # Tenta abrir a pasta logs, caso não exista ele cria a pasta desafio
        try:
            pastaDesafio = open(ROOT_PATH/"logs"/"log.txt")
        except Exception as exc:
            print(f"Pasta não existia, criando agora...")
            os.mkdir(ROOT_PATH/'logs')
            

        # Cria o arquivo log.txt dentro da pasta desafio    
        with open(ROOT_PATH/'logs'/'log.txt','a') as arquivo:
            try:
                arquivo.write(texto)
            except Exception as exc:
                print(f"Error: {exc}")
        return resultado
    return envelope

# Gerador



###################################################################################################
def menu():
    menu =  """
                Menu                   
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [nc] Nova conta
    [lc] Listar contas
    [nu] Novo usuário
    [q] Sair

    => """
    return input(menu)

def main():
    clientes = []
    contas = []
 
    
    while True:
        opcao = menu()
        
        if opcao == 'd':
           depositar(clientes)

        elif opcao == 's':
           sacar(clientes)

        elif opcao == 'e':
            exibir_extrato(clientes)

        elif opcao == 'nu':
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas)+1
            criar_conta(numero_conta,clientes,contas)

        elif opcao == 'lc':
            listar_contas(contas)

        elif opcao == 'q':
            break
        else:
            print("Opção inválida, por favor selecione novamente a operação desejada")



# funçoes
def criar_usuario(usuarios):
    cpf = input("Informe o cpf (somente número): ")
    usuario = filtrar_cliente(cpf,usuarios)
    
    if usuario:
        print(" Já existe usuario cadastrado com esse CPF! ")
        return
    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe  a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    usuarios.append({"nome":nome,"data_nascimento":data_nascimento,"cpf":cpf,"endereco":endereco})

    print("  Usuario criado com sucesso !")


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente._cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print(" Cliente não possui conta!")
        return
    return cliente.contas[0]


@log_transacao
def criar_conta(numero_conta, clientes,contas):
    cpf = input("Informe o CPF do usuário: ")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print("Cliente não encontrado, fluxo de criação de conta encerrado!")
        return
    
    conta = ContaCorrente.nova_conta(numero=numero_conta,cliente=cliente)
    contas.append(conta)
    cliente.contas.append(conta)

    print("Conta criada com sucesso!")


@log_transacao
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return
    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta,transacao)
    

@log_transacao    
def depositar(clientes):
    cpf = input("Informe o CPF do Cliente: ")
    cliente = filtrar_cliente(cpf,clientes)
    if not cliente:
        print(" Cliente não encontrado! ")
        return
    valor = float(input("Informe o valor do depósito:"))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta,transacao)
     

@log_transacao
def exibir_extrato(clientes):
    cpf = input("Informe o CPF do Cliente: ")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print(" Cliente não encontrado! ")
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    print("================EXTRATO================")
    extrato = ""
    tem_transacao = False
    for transacao in conta.historico.gerar_relatorio():
        tem_transacao = True
        extrato += f"\n{transacao['tipo']}:\nR$ {transacao['valor']:.2f}"
    if not tem_transacao:
        extrato = "Não foram realizadas movimentaçoes"

    print(extrato)
    print(f"\nSaldo:\n R$ {conta.saldo:.2f}")
    print({'='*100})


@log_transacao
def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente números): ")
    cliente = filtrar_cliente(cpf,clientes)

    if cliente:
        print("Já existe cliente com esse CPF cadastrado")
        return
    
    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (Logradouro,nro - Bairro - Cidade/Sigla do Estado): ")

    cliente = PessoaFisica(nome=nome,data_nascimento=data_nascimento,cpf=cpf,endereco=endereco)

    clientes.append(cliente)

    print("Cliente criado com sucesso !! ")


def listar_contas(contas):
    for i in ContaIterador(contas):
        print(i)
    # for conta in contas:
    #     print("="*100)
    #     print(str(conta))
        

main()



# testes realizados

# Criando o cliente 

# c1 = PessoaFisica(654789123,"Harry","06/12/2000","Hogwarts")

# # Pegando os dados do cliente

# print(c1.getDados())

# # Criando as contas do cliete

# conta = ContaCorrente(c1._nome,123)

# conta2 = Conta(c1._nome,432)

# # vinculando as contas ao cliente C1

# c1.adicionar_conta(conta)
# c1.adicionar_conta(conta2)

# #vizualizando todas as contas vinculados ao cliente c1
# c1.getContas()

# # Testando os depositos e saques

# deposito = Deposito(1000)
# deposito.registrar(conta)

# depositoC2 = Deposito(534)
# depositoC2.registrar(conta2)

# saque = Saque(125)
# saque.registrar(conta)

# saqueC2 = Saque(421)
# saqueC2.registrar(conta2)


# #vizualizando todas as contas vinculados ao cliente c1 depois de um deposito
# c1.getContas()

