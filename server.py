import socket

def iniciar_servidor():
    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_servidor.bind(('localhost', 12345))
    socket_servidor.listen(1)
    print("Servidor aguardando conexão...")

    socket_cliente, endereco_cliente = socket_servidor.accept()
    print(f"Conexão estabelecida com {endereco_cliente}")

    dados = socket_cliente.recv(1024).decode()
    print(f"Dados recebidos do cliente: {dados}")

    resposta = f"Modo: operação padrão, Tamanho máximo: {dados.split()[-2]} caracteres"
    socket_cliente.send(resposta.encode())

    print(f"Handshaking completo! Servidor enviado: {resposta}")

    socket_cliente.close()
    socket_servidor.close()

if __name__ == "_main_":
    iniciar_servidor()