import socket

def iniciar_cliente():
    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_cliente.connect(('localhost', 12345))

    tamanho_maximo = input("Digite o tamanho máximo de caracteres desejado: ")
    dados_para_enviar = f"Modo: operação padrão, Tamanho máximo: {tamanho_maximo} caracteres"
    
    socket_cliente.send(dados_para_enviar.encode())
    print(f"Cliente enviou: {dados_para_enviar}")

    resposta = socket_cliente.recv(1024).decode()
    print(f"Resposta do servidor: {resposta}")

    socket_cliente.close()

if __name__ == "_main_":
    iniciar_cliente()