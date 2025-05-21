import socket

def calcular_checksum(payload):
    return sum(ord(c) for c in payload) % 256

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('localhost', 12345))
    servidor.listen(1)
    print("Aguardando conexão do cliente...")

    cliente, endereco = servidor.accept()
    print(f"Conectado com {endereco}")

    handshake = cliente.recv(1024).decode()
    print(f"[Handshake] -> {handshake}")

    
    try:
        partes = handshake.split(",")
        max_caracteres = int(partes[1].strip().split()[-1])
        janela = int(partes[2].strip().split()[-1])
    except Exception:
        max_caracteres = 3
        janela = 1

    
    modo_confirmacao = input("Modo de confirmação do servidor? (1=individual, 2=em grupo): ")
    modo_confirmacao = int(modo_confirmacao) if modo_confirmacao in ['1','2'] else 1

    confirmacao_inicial = f"Configuração recebida. Máximo: {max_caracteres} caracteres, Janela: {janela}, Modo confirmação: {modo_confirmacao}"
    cliente.send(confirmacao_inicial.encode())
    print("Handshake finalizado. Aguardando pacotes...\n")

    mensagem_final = ""
    buffer = {}
    esperado_seq = 0

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
            buffer[num_seq] = payload
            
            if modo_confirmacao == 1:
                ack_msg = f"ACK {num_seq}"
                cliente.send(ack_msg.encode())
                print(f"[Servidor] Enviado {ack_msg}")

            
            elif modo_confirmacao == 2:
                
                if num_seq == esperado_seq:
                    
                    while esperado_seq in buffer:
                        mensagem_final += buffer[esperado_seq]
                        del buffer[esperado_seq]
                        esperado_seq += 1
                    ack_msg = f"ACK {esperado_seq - 1}"
                    cliente.send(ack_msg.encode())
                    print(f"[Servidor] Enviado {ack_msg}")
        else:
            nak_msg = f"NAK {num_seq}"
            cliente.send(nak_msg.encode())
            print(f"[Servidor] Enviado {nak_msg}")

    
    if modo_confirmacao == 2:
        for seq in sorted(buffer):
            mensagem_final += buffer[seq]

    print("\nMensagem completa recebida:")
    print(mensagem_final)

    cliente.close()
    servidor.close()

if _name_ == "_main_":
    iniciar_servidor()
