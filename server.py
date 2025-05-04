import socket

def calcular_checksum(payload):
    """Calcula o checksum simples somando os valores ASCII dos caracteres."""
    return sum(ord(c) for c in payload) % 256 #(pra nao passar de 1 byte )

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('localhost', 12345))
    servidor.listen(1)
    print("Aguardando conexão do cliente...")

    cliente, endereco = servidor.accept()
    print(f"Conectado com {endereco}")

    handshake = cliente.recv(1024).decode()
    print(f"[Handshake] -> {handshake}")

    max_caracteres = handshake.split()[-2]
    confirmacao_inicial = f"Configuração recebida. Máximo: {max_caracteres} caracteres por pacote."
    cliente.send(confirmacao_inicial.encode())
    print("Handshake finalizado. Aguardando pacotes...\n")

    mensagem_final = ""
    contador_pacote = 0

    while True:
        trecho = cliente.recv(1024).decode()
        if trecho == "FIM":
            break

        if not trecho.startswith('D'):
            continue  

        num_seq = int(trecho[1])
        payload = trecho[2:-3]
        checksum_recebido = int(trecho[-3:])

        checksum_calculado = calcular_checksum(payload)

        print(f"Pacote recebido:")
        print(f"  Número de Sequência: {num_seq}")
        print(f"  Payload: '{payload}'")
        print(f"  Checksum recebido: {checksum_recebido}, Checksum calculado: {checksum_calculado}")

        if checksum_calculado == checksum_recebido:
            mensagem_final += payload
            ack_msg = f"ACK {num_seq}"
            cliente.send(ack_msg.encode())
        else:
            nak_msg = f"NAK {num_seq}"
            cliente.send(nak_msg.encode())

    print("\nMensagem completa recebida:")
    print(mensagem_final)

    cliente.close()
    servidor.close()

if _name_ == "_main_":
    iniciar_servidor()
