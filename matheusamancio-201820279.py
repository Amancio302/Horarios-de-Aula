#coding: utf-8
import xlrd #biblioteca para ler arquivo xls
import datetime

numPrefs = 0		#Variável que controla a quantidade total de preferências de professores
numPrefAtendidas = 0

def Escola(escola):
	Vertices = [] 		#Lista contendo todos os vértices, Genéricos ou MTPs
	Configuracoes = [] 	#Lista contendo todos os horários da escola
	Materias = [] 		#Lista contendo todas as matérias cadastradas
	Turmas = [] 		#Lista contendo todas as turmas cadastradas
	Professores = [] 	#Lista contendo todos os profesores cadastrados
	MTPs = [] 			#Lista contendo todas as referências de MTPs contidas na lista Vertices
	Preferencias = [] 	#Lista contendo as preferências não atendidas
	

	#Função que retorna um valor para cada dia, a partir de uma string com seu nome

	def getDia(dia):
		if(dia == "Segunda"):
			dia = 0
		elif(dia == "Terça"):
			dia = 1
		elif(dia == "Quarta"):
			dia = 2
		elif(dia == "Quinta"):
			dia = 3
		elif(dia == "Sexta"):
			dia = 4
		else:
			dia = -1
		return dia

	#Função que busca a configuração dos horários na planilha e retorna valores de 0 a n
	#para cada horário da planilha 
		
	def getHorario(horario):
		for i in range(len(Configuracoes)):
			if(horario == Configuracoes[i]):
				return i
		return -1
		
	# Classe horário, que possui os atributos "dia", "horário" e "cor", classe que verifica a validade
	# dos dados que estão entrando e atribui uma união de strings para determinar a cor
	# além disso, possui um método mágico para sobrecarregar o operador de soma	
				
	class Horario:
		def __init__(self, diaStr, horarioStr):
			dia = getDia(diaStr)
			horario = getHorario(horarioStr)
			if(dia > 5 or dia < 0 or horario < 0 or horario > len(Configuracoes)):
				self.dia = dia
				self.horario = horario
			else:
				self.dia = -1
				self.horario = -1
			self.cor = str(dia) + "/" + str(horario)
		def __add__(self):
			if(self.dia <= 5):
				self.dia += 1
			elif(horario < len(Configuracoes)):
				self.horario += 1
				self.dia = 1
			else:
				self.dia = -1
				self.horario = -1
			self.cor = str(self.dia) + "/" + str(self.horario)

	# Classe Vertice, esta inicializa um vértice do grafo, possui um iD, sua cor obtida da classe Horario
	# e a sua lista de adjacência. É a classe mais genérica utilizada para instanciação de 'vértices de 
	# restrição', utilizados na parte de restrições do projeto

	class Vertice:
		idVertice = 0
		def __init__(self):
			self.horario = Horario(0, 0)
			self.adjacencia = []
			self.idVertice = Vertice.idVertice
			Vertice.idVertice += 1

	# Classe Professor, feita para a instância dos professores no problema, possuem um iD do professor e
	# seu nome. Além disso, há também duas Listas que são as restrições e as preferências do docente.

	class Professor:
		idProfessor = 0
		def __init__(self, nome):
			self.nome = nome
			self.idProfessor = Professor.idProfessor
			Professor.idProfessor += 1
			self.restricao = []
			self.preferencia = []

	# Classe Matéria, feita para a instância das matérias da escola, possuem um iD para identificação
	# e seu nome.

	class Materia:
		idMateria = 0
		def __init__(self, nome):
			self.nome = nome
			self.idMateria = Materia.idMateria
			Materia.idMateria += 1

	# Classe Turma, feita para a instância das turmas da escola, possuem um iD para identificação, além
	# do nome da turma e de uma lista com suas restrições.
	class Turma:
		idTurma = 0
		def __init__(self, nome):
			self.nome = nome
			self.idTurma = Turma.idTurma
			Turma.idTurma += 1
			self.restricao = []

	# Classe MTP, uma herança da classe vértice, em que se instanciam vértices que possuem as informações
	# de Matéria, Turma e Professor (através de seus iDs), são basicamentes vértices que juntam as características
	# das 3 classes acima citadas

	class MTP(Vertice):
		
		# Método de inicialização da MTP
		
		def __init__(self, idMateria, idTurma, idProfessor):
			self.idMateria = idMateria
			self.idTurma = idTurma
			self.idProfessor = idProfessor
			self.geminada = False
			super().__init__()
		
		# Método feito para conceder uma cor aos vértices com base em suas adjacências 
		
		def recebeCor(self, cor):
			for a in self.adjacencia:
				if(Vertices[a].horario.cor == cor):
					return False
			self.horario.cor = cor
			return True

	# O seguinte método cria as listas de adjacências de cada vértice(MTP), verificando com 2
	# laços de repetição se o seu par possui alguma turma em comum ou algum professor em comum
	# fazendo com que estes não possam ser pintados com a mesma cor, adicionando-os em suas 
	# respectivas listas de adjacências 

	def criaListaAdj():
		for idV1 in MTPs:
			for idV2 in MTPs:
				if(idV1 != idV2):
					if(Vertices[idV1].idTurma == Vertices[idV2].idTurma or Vertices[idV1].idProfessor == Vertices[idV2].idProfessor):
						Vertices[idV1].adjacencia.append(idV2)

	# O método a seguir adiciona ás listas de adjacencias dos vértices(MTPs) as restrições que
	# foram obtidas através do arquivo, fazendo com que os vértices tenham cores diferentes dos
	# casos onde essas restrições ocorrem

	def addRestricao():
		for idV in MTPs:
			for t in Turmas:
				if(Vertices[idV].idTurma == t.idTurma):
					for restricao in t.restricao:
						Vertices[idV].adjacencia.append(restricao)
			for p in Professores:
				if(Vertices[idV].idProfessor == p.idProfessor):
					for restricao in p.restricao:
						Vertices[idV].adjacencia.append(restricao)	

	def addPreferencias():
		numProfs = len(Professores)
		global numPrefAtendidas
		# Enquanto houverem preferências passíveis de resolução
		while(numPrefAtendidas + len(Preferencias) < numPrefs):
			lastProfId = -1
			# Busca nos vértices MTPs
			for v in MTPs:
				# Se o vértice não tiver cor
				if(Vertices[v].horario.cor == "-1/-1"):
					# Se o professor atual não foi o último atendido
					if(Vertices[v].idProfessor != lastProfId):
						# Procura em suas preferências alguma que pode encaixar com o vértice
						for pref in Professores[Vertices[v].idProfessor].preferencia:
							# Caso consiga encaixar
							if(Vertices[v].recebeCor(pref.cor)):
								# Atualiza os valores para controle
								numPrefAtendidas += 1
								lastProfId = Vertices[v].idProfessor
								if(pref in Preferencias):
									Preferencias.remove(pref)
								Professores[Vertices[v].idProfessor].preferencia.remove(pref)
								break
							else:
								if(pref not in Preferencias):
									Preferencias.append(pref)
				

	# Todo o método a seguir foi feito para puxar os dados da planilha fornecida com os dados
	# e possibilitar a manipulação e testes do problema através desses, a biblioteca utilizada
	# para isso foi a xlrd

	def leDoArquivo(escola):
		# Abre o arquivo
		wb = xlrd.open_workbook(escola)
		ws = wb.sheet_by_index(0)
		for i in range(ws.nrows):
			# Ignora linha de cabeçalho
			if i == 0:
				continue
			else:
				materiaNome = ws.cell(i, 0).value
				turmaNome = str(ws.cell(i, 1).value)
				professorNome = ws.cell(i, 2).value
				qtd = ws.cell(i, 3).value
				
				matId = 0
				if(len(Materias) != 0):
					existe = False
					for materia in Materias:
						if(materiaNome == materia.nome):
							existe = True
							matId = materia.idMateria
					if(not existe):
						materia = Materia(materiaNome)
						matId = materia.idMateria
						Materias.append(materia)
				else:
					Materias.append(Materia(materiaNome))
					
				turmaId = 0
				if(len(Turmas) != 0):
					existe = False
					for turma in Turmas:
						if(turmaNome == turma.nome):
							existe = True
							turmaId = turma.idTurma
							break
					if(not existe):
						turma = Turma(turmaNome)
						turmaId = turma.idTurma
						Turmas.append(turma)
				else:
					Turmas.append(Turma(turmaNome))
					
				professorId = 0
				if(len(Professores) != 0):
					existe = False
					for professor in Professores:
						if(professorNome == professor.nome):
							existe = True
							professorId = professor.idProfessor
							break
					if(not existe):
						professor = Professor(professorNome)
						professorId = professor.idProfessor
						Professores.append(professor)
				else:
					Professores.append(Professor(professorNome))
					
				for i in range(int(qtd)):
					mtp = MTP(matId, turmaId, professorId)
					Vertices.append(mtp)
					MTPs.append(mtp.idVertice)
		
		# Obtém os dados da Planilha Configuracoes
				
		ws = wb.sheet_by_index(1)
		for i in range(ws.nrows):
			if i == 0:
				continue
			else:
				Configuracoes.append(ws.cell(i, 0).value)

		#
		ws = wb.sheet_by_index(2)
		for i in range(ws.nrows):
			if i == 0:
				continue
			else:
				professor = ws.cell(i, 0).value
				for p in Professores:
					if(p.nome == professor):
						v = Vertice()
						v.horario = Horario(ws.cell(i, 2).value, ws.cell(i, 1).value)
						Vertices.append(v)
						p.restricao.append(v.idVertice)
						break

		ws = wb.sheet_by_index(3)
		for i in range(ws.nrows):
			if i == 0:
				continue
			else:
				turma = str(ws.cell(i, 0).value)
				for t in Turmas:
					if(t.nome == turma):
						v = Vertice()
						v.horario = Horario(ws.cell(i, 2).value, ws.cell(i, 1).value)
						Vertices.append(v)
						t.restricao.append(v.idVertice)
						break

		ws = wb.sheet_by_index(4)
		global numPrefs
		for i in range(ws.nrows):
			if i == 0:
				continue
			else:
				professor = ws.cell(i, 0).value
				for p in Professores:
					if(p.nome == professor):
						h = Horario(ws.cell(i, 2).value, ws.cell(i, 1).value)
						p.preferencia.append(h)
						numPrefs += 1
						break

	def main(escola):
		global numPrefAtendidas, numPrefs
		numPrefs = 0
		numPrefAtendidas = 0
		leDoArquivo(escola)
		criaListaAdj()
		addRestricao()
		addPreferencias()
		print(numPrefs, "/", numPrefAtendidas, "/", len(Preferencias))
	main(escola)


Escola("Escola_A.xlsx")
Escola("Escola_B.xlsx")
Escola("Escola_C.xlsx")
Escola("Escola_D.xlsx")
