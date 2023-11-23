import multiprocessing
import time

# Variáveis compartilhadas para indicar se uma eleição está em andamento e quem é o coordenador
eleicao_em_andamento = multiprocessing.Value('b', False)
coordenador = multiprocessing.Value('i', 7)

class Processo(multiprocessing.Process):
    def __init__(self, id, pipe_in, pipe_out):
        super(Processo, self).__init__()
        self.id = id
        self.pipe_in = pipe_in
        self.pipe_out = pipe_out
        self.participante = False  # Indica se o processo está participando da eleição

    def run(self):
        start_time = time.time()
        while time.time() - start_time < 15:  # O processo executa por 15 segundos
            if self.id == coordenador.value:  # Se o processo é o coordenador
                print(f"Processo {self.id} agora é o coordenador.")
                time.sleep(1)
            else:  # Se o processo não é o coordenador
                print(f"Processo {self.id} enviando mensagem de teste para o coordenador.")
                self.pipe_out.send(('teste', self.id))  # Envia uma mensagem de teste para o coordenador
                time.sleep(1)
                if self.pipe_in.poll():  # Se há uma mensagem no pipe
                    msg, id = self.pipe_in.recv()  # Recebe a mensagem
                    if msg == 'eleição':  # Se a mensagem é de eleição
                        print(f"Processo {self.id} recebeu mensagem de eleição.")
                        if self.id > id and not self.participante:  # Se o id do processo é maior e ele não está participando
                            self.participante = True  # Marca o processo como participante
                            self.pipe_out.send(('eleição', self.id))  # Envia uma mensagem de eleição com seu id
                        else:
                            self.pipe_out.send(('eleição', id))  # Encaminha a mensagem de eleição
                    elif msg == 'eleito':  # Se a mensagem é de eleito
                        if id == self.id:
                            coordenador.value = self.id  # Atualiza o valor do coordenador
                        self.participante = False  # Marca o processo como não participante
                        eleicao_em_andamento.value = False  # Indica que a eleição terminou
                        self.pipe_out.send(('eleito', id))  # Encaminha a mensagem de eleito
                elif not eleicao_em_andamento.value:  # Se não há uma eleição em andamento
                    print(f"Processo {self.id} não recebeu resposta do coordenador. Iniciando eleição.")
                    self.participante = True  # Marca o processo como participante
                    eleicao_em_andamento.value = True  # Indica que uma eleição está em andamento
                    self.pipe_out.send(('eleição', self.id))  # Envia uma mensagem de eleição

def criar_processos(n):
    pipes = [multiprocessing.Pipe(False) for _ in range(n)]  # Cria os pipes para comunicação
    processos = []
    for i in range(n):  # Cria os processos
        p = Processo(i+1, pipes[i-1][0], pipes[i][1])
        p.start()
        processos.append(p)
    return processos

def simular_falha(processos, id):
    for p in processos:  # Procura o processo com o id especificado
        if p.id == id:
            p.terminate()  # Termina o processo para simular uma falha
            print(f"Processo {id} terminado.")
            time.sleep(1)  # Espera um segundo para garantir que a mensagem seja impressa antes da eleição começar

def main():
    processos = criar_processos(7)  # Cria 7 processos
    time.sleep(5)  # Espera 5 segundos
    simular_falha(processos, 7)  # Simula uma falha no processo 7
    time.sleep(10)  # Espera 10 segundos
    for p in processos:  # Termina todos os processos
        if p.is_alive():  # Verifica se o processo está vivo antes de tentar terminá-lo
            p.terminate()

if __name__ == "__main__":
    main()
