import socket
import time

def calcular_checksum(payload):
    """Calcula o checksum simples somando os valores ASCII dos caracteres."""
    return sum(ord(c) for c in payload) % 256

def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('localhost', 12345))
    cliente.settimeout(2)  # Tempinho de 2 segundos para receber ACK/NAK(certo ou errado)

    max_pacote = 3  
    dados_iniciais = f"Modo: operação padrão, Tamanho máximo: {max_pacote} caracteres"
    cliente.send(dados_iniciais.encode())
    print(f"[Cliente] Enviado: {dados_iniciais}")

    resposta = cliente.recv(1024).decode()
    print(f"[Servidor] {resposta}\n")

    mensagem = input("Digite a mensagem para envio: ")
    blocos = [mensagem[i:i+max_pacote] for i in range(0, len(mensagem), max_pacote)]

    num_sequencia = 0

    for idx, bloco in enumerate(blocos):
        checksum = calcular_checksum(bloco)
        pacote = f"D{num_sequencia}{bloco}{checksum:03}"  
        enviado = False

        while not enviado:
            cliente.send(pacote.encode())
            print(f"Enviando bloco {idx+1}: '{bloco}' com Seq={num_sequencia} e Checksum={checksum}")

            try:
                resposta = cliente.recv(1024).decode()
                print(f"-> Resposta do servidor: {resposta}")

                if resposta.startswith("ACK") and int(resposta.split()[1]) == num_sequencia:
                    enviado = True  # Foi confirmado
                    num_sequencia += 1
                elif resposta.startswith("NAK"):
                    print("-> Recebido NAK, reenviando pacote")
            except socket.timeout:
                print("-> Timeout! Reenviando pacote...")

    cliente.send("FIM".encode())
    print("\nMensagem enviada por completo. Finalizando conexão.")

    cliente.close()

if _name_ == "_main_":
    iniciar_cliente()
