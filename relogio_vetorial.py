import socket
import pickle
import random
import time
import threading


class Process:
    def __init__(self, pid: int, total_process: int = 4) -> None:
        self.pid = pid
        self.total_process = total_process
        self.vector_clock = [0] * total_process
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('localhost', 5000 + pid))
            self.socket.listen()
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
            print(f"Processo {self.pid} iniciado e vinculado à porta {5000 + pid}")
        except Exception as e:
            print(f"Erro ao iniciar o processo {self.pid}: {e}")

    def send_message(self) -> None:
        # Enviar mensagem para um processo aleatório
        recipient_pid = random.randint(0, self.total_process - 1)
        if recipient_pid == self.pid:
            return

        # Incrementar relógio do processo e gerar mensagem
        self.vector_clock[self.pid] += 1
        message = (self.pid, self.vector_clock.copy())

        # Conectar ao destinatário e enviar a mensagem
        recipient_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recipient_socket.connect(('localhost', 5000 + recipient_pid))
        recipient_socket.sendall(pickle.dumps(message))
        recipient_socket.close()

        # Imprimir vetor enviado
        print(f"Processo {self.pid}: Vetor enviado: {self.vector_clock}")

    def receive_messages(self) -> None:
        while True:
            conn, addr = self.socket.accept()
            data = conn.recv(4096)

            # Extrair informações da mensagem
            sender_pid, sender_vector_clock = pickle.loads(data)

            # Atualizar vetor local
            for p in range(self.total_process):
                self.vector_clock[p] = max(self.vector_clock[p], sender_vector_clock[p])

            # Imprimir informações relevantes
            print()
            print(f"Processo {self.pid}: Vetor recebido do processo {sender_pid}: {sender_vector_clock}")
            print(f"Processo {self.pid}: Vetor próprio antes da atualização: {self.vector_clock}")
            
            # Atualizar vetor próprio
            self.vector_clock[self.pid] += 1
            print(f"Processo {self.pid}: Vetor atualizado: {self.vector_clock}")

            conn.close()


# Definir número de processos
process_count = 4

# Criar e iniciar processos
processes = []
for i in range(process_count):
    process = Process(i, process_count)
    if process.socket:
        processes.append(process)

# Simular envio aleatório de mensagens
while True:
    for process in processes:
        # Enviar mensagem com intervalo aleatório
        time.sleep(random.uniform(1, 4))
        process.send_message()


