import socket
import time

def calcular_checksum(payload):
    return sum(ord(c) for c in payload) % 256

def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('localhost', 12345))
    cliente.settimeout(2)

    max_pacote = 3
    janela_tamanho = 2  

    dados_iniciais = f"Modo: padrão, Tamanho: {max_pacote}, Janela: {janela_tamanho}"
    cliente.send(dados_iniciais.encode())
    print(f"[Cliente] Enviado: {dados_iniciais}")

    resposta = cliente.recv(1024).decode()
    print(f"[Servidor] {resposta}\n")

    mensagem = input("Digite a mensagem: ")
    blocos = [mensagem[i:i+max_pacote] for i in range(0, len(mensagem), max_pacote)]

    erro_indices = input("Índices dos blocos com ERRO (ex: 1,3): ")
    perda_indices = input("Índices dos blocos com PERDA (ex: 2): ")
    erro_indices = [int(i) for i in erro_indices.split(",") if i.strip().isdigit()]
    perda_indices = [int(i) for i in perda_indices.split(",") if i.strip().isdigit()]

    base = 0
    num_sequencia = 0
    enviados = {}

    while base < len(blocos):
        
        while len(enviados) < janela_tamanho and base + len(enviados) < len(blocos):
            idx = base + len(enviados)
            bloco = blocos[idx]
            checksum = calcular_checksum(bloco)

            if idx in erro_indices:
                checksum = (checksum + 1) % 256  # Força erro
                print(f"[Simulação] ERRO no bloco {idx} (checksum alterado)")

            pacote = f"D{num_sequencia}{bloco}{checksum:03}"

            if idx in perda_indices:
                print(f"[Simulação] PERDA no bloco {idx} (não enviado)")
            else:
                cliente.send(pacote.encode())
                print(f"[Cliente] Enviando bloco {idx}: '{bloco}' Seq={num_sequencia} Checksum={checksum}")

            enviados[idx] = (pacote, num_sequencia, bloco)
            num_sequencia += 1

        
        try:
            resposta = cliente.recv(1024).decode()
            print(f"-> Resposta do servidor: {resposta}")

            if resposta.startswith("ACK"):
                ack_seq = int(resposta.split()[1])
                
                confirmados = [idx for idx, (_, seq, _) in enviados.items() if seq == ack_seq]
                for idx in confirmados:
                    print(f"[Cliente] ACK recebido para bloco {idx}")
                    enviados.pop(idx)
                    base += 1

            elif resposta.startswith("NAK"):
                nak_seq = int(resposta.split()[1])
                print(f"[Cliente] NAK recebido (Seq={nak_seq}). Reenviando pacote.")
                for idx, (pacote, seq, bloco) in enviados.items():
                    if seq == nak_seq:
                        cliente.send(pacote.encode())
                        print(f"[Cliente] Reenvio do bloco {idx}: '{bloco}' Seq={seq}")
                        break
        except socket.timeout:
            print("-> Timeout! Reenviando todos os pacotes da janela.")
            for idx, (pacote, seq, bloco) in enviados.items():
                cliente.send(pacote.encode())
                print(f"[Cliente] Reenvio por timeout do bloco {idx}: '{bloco}' Seq={seq}")

    cliente.send("FIM".encode())
    print("\nMensagem enviada por completo. Finalizando conexão.")
    cliente.close()

if _name_ == "_main_":
    iniciar_cliente()
