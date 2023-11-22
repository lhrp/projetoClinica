import sqlite3, bcrypt, os, random, string
from datetime import datetime

# Caminho do arquivo .db
DB_PATH = "liteDatabase/clinica.db"

# Função para verificar e criar as tabelas no banco de dados
def criar_tabelas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de Médicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbFuncionario (
            nCdFuncionario INTEGER PRIMARY KEY AUTOINCREMENT,
            cNomeFuncionario TEXT NOT NULL,
            cEspecialidade TEXT NOT NULL,
            cEmail TEXT NOT NULL,
            cLogin TEXT NOT NULL,
            cSenha TEXT NOT NULL
        )
    ''')

    # Tabela de Mães
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbMae (
            nCdMae INTEGER PRIMARY KEY AUTOINCREMENT,
            cNomeMae TEXT NOT NULL,
            cCPF TEXT NOT NULL,
            dtNascimento DATE NOT NULL,
            cEndereco TEXT,
            cNumero TEXT,
            cEmail TEXT NOT NULL
        )
    ''')

    # Tabela de Dados Auxiliares
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbMaeAux (
            nCdMae INTEGER,
            nCdFuncionario TEXT DEFAULT "Não Definido",
            cEmailContato TEXT DEFAULT "Não Informado",
            FOREIGN KEY (nCdMae) REFERENCES tbMae (nCdMae),
            FOREIGN KEY (nCdFuncionario) REFERENCES tbFuncionario (nCdFuncionario)
        )
    ''')

    # Tabela de Crianças
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbCrianca (
            nCdCrianca INTEGER PRIMARY KEY AUTOINCREMENT,
            cNomeCrianca TEXT NOT NULL,
            dtNascimento DATE,
            nCdMae INTEGER,
            nCdCodigoCrianca TEXT NOT NULL,
            FOREIGN KEY (nCdMae) REFERENCES tbMae (nCdMae)
        )
    ''')

    # Tabela de Dados Auxiliares da Crianças
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbProntuario (
            nCdProntuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nCdCrianca INTEGER NOT NULL,
            nPeso REAL NOT NULL,
            nAltura REAL NOT NULL,
            nPressao REAL NOT NULL,
            nTemperatura REAL NOT NULL,
            dtProntuario DATE NOT NULL,
            cHorario TEXT NOT NULL,
            nCdFuncionario INTEGER NOT NULL,
            cObservacao TEXT NOT NULL,
            FOREIGN KEY (nCdCrianca) REFERENCES tbCrianca (nCdCrianca)
        )
    ''')

    conn.commit()
    conn.close()

# Função para cadastrar um Funcionário
def cadastrarFuncionario(cNomeFuncionario, cEspecialidade, cEmail, cLogin, cSenha):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cSenha = bcrypt.hashpw(cSenha.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("INSERT INTO tbFuncionario (cNomeFuncionario, cEspecialidade, cEmail, cLogin, cSenha) VALUES (?, ?, ?, ?, ?)", (cNomeFuncionario, cEspecialidade, cEmail, cLogin, cSenha.decode('utf-8')))
        conn.commit()
    except:
        pass

    conn.close()

def validaLoginFuncionario(cLoginEmail):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT nCdFuncionario
                            , cLogin
                            , cEmail
                            , cSenha 
                         FROM tbFuncionario
                        WHERE (cLogin = '{cLoginEmail}' OR cEmail = '{cLoginEmail}')""")
    user = cursor.fetchone()
    if user == None:
        conn.close()
        return 0
    else:
        conn.close()
        return user
    

# Função para listar todos os Funcionários
def listarFuncionarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tbFuncionario WHERE cEspecialidade <> 'Administrador'")
    funcionarios = cursor.fetchall()
    conn.close()

    return funcionarios

# Função para listar todos os Funcionários
def dadosFuncionarioLogado(nCdFuncionario):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM tbFuncionario WHERE nCdFuncionario = {nCdFuncionario}")
    funcionarios = cursor.fetchall()
    conn.close()

    return funcionarios

# Função para cadastrar uma mãe
def cadastrarMae(cNomeMae, cCPF, dtNascimento, cEndereco, cNumero, cEmail):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO tbMae (cNomeMae, cCPF, dtNascimento, cEndereco, cNumero, cEmail) VALUES (?, ?, ?, ?, ?, ?)", (cNomeMae, cCPF, dtNascimento, cEndereco, cNumero, cEmail))
        conn.commit()
    except:
        pass

    conn.close()

def atualizarMae(nCdMae, cEndereco, cNumero, cEmail):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(f"""UPDATE tbMae  
                            SET cEndereco = {cEndereco}
                              , cNumero = {cNumero}
                              , cEmail = '{cEmail}' 
                          WHERE nCdMae = {nCdMae}""")
        conn.commit()
    except:
        pass

    conn.close()

# Função para listar todas as mães
def listarMaes(nCdMae):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM tbMae WHERE nCdMae = {nCdMae}")
    maes = cursor.fetchall()
    conn.close()

    return maes

def listarMaesBase(cNomeMae, cCPF):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT nCdMae FROM tbMae WHERE cNomeMae = '{cNomeMae}' AND cCPF = '{cCPF}'")
    codigoMae = cursor.fetchone()
    conn.close()

    return codigoMae

# Função para cadastrar os dados auxiliares de uma mãe
def cadastrarMaeAux(nCdMae, nCdFuncionario, cEmailContato):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO tbMaeAux (nCdMae, nCdFuncionario, cEmailContato) VALUES (?, ?, ?)", (nCdMae, nCdFuncionario, cEmailContato))
        conn.commit()
    except:
        pass

    conn.close()


def cadastrarMaeAuxBase(nCdMae):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO tbMaeAux (nCdMae) VALUES (?)", (nCdMae))
        conn.commit()
    except:
        pass

    conn.close()


def atualizarMaeAux(nCdMae, nCdFuncionario, cEmailContato):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(f"UPDATE tbMaeAux SET nCdFuncionario = {nCdFuncionario}, cEmailContato = '{cEmailContato}' WHERE nCdMae = {nCdMae}")
        conn.commit()
    except:
        pass

    conn.close()

# Função para listar todos os dados auxiliares das mães
def listarMaesAuxi(nCdMae):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM tbMaeAux WHERE nCdMae = {nCdMae}")
    maes = cursor.fetchall()
    conn.close()
    return maes

def listarMaesAux():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
                    SELECT tbMae.nCdMae 
                        , tbMae.cNomeMae
                        , strftime('%d/%m/%Y', tbMae.dtNascimento) as dtNascimento
                        , tbMae.cEmail
                        , tbMaeAux.cEmailContato
                        , tbFuncionario.cNomeFuncionario
                        , tbFuncionario.cEspecialidade
                    FROM tbMae
                    LEFT JOIN tbMaeAux ON tbMaeAux.nCdMae = tbMae.nCdMae
                    LEFT JOIN tbFuncionario ON tbFuncionario.nCdFuncionario = tbMaeAux.nCdFuncionario;
                    """)
    dadosMaes = cursor.fetchall()
    conn.close()

    return dadosMaes

def gerarCodigoCrianca():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# Função para cadastrar uma criança
def cadastrarCrianca(cNomeCrianca, dtNascimento, nCdMae):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO tbCrianca (cNomeCrianca, dtNascimento, nCdMae, nCdCodigoCrianca) VALUES (?, ?, ?, ?)",
                       (cNomeCrianca, dtNascimento, nCdMae, gerarCodigoCrianca()))
        conn.commit()
    except:
        pass

    conn.close()

# Função para listar todas as crianças
def listarCriancas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT nCdCrianca, cNomeCrianca, strftime('%d/%m/%Y', tbCrianca.dtNascimento) as dtNascimento, cNomeMae, nCdCodigoCrianca FROM tbCrianca INNER JOIN tbMae ON tbMae.nCdMae = tbCrianca.nCdMae")
    criancas = cursor.fetchall()
    conn.close()

    return criancas

def buscarCriancaCodigoGerado(nCdCodigoCrianca):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT nCdCrianca, cNomeCrianca FROM tbCrianca WHERE nCdCodigoCrianca = '{nCdCodigoCrianca}'")
    criancas = cursor.fetchall()
    conn.close()

    return criancas

# Função para cadastrar os dados auxliares de uma criança
def cadastrarCriancaAux(nCdCrianca, nPeso, nAltura, nPressao, nTemperatura, dtProntuario, nCdFuncionario, cObservacao):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    horarioProntuario = datetime.now()
    try:
        cursor.execute("INSERT INTO tbProntuario (nCdCrianca, nPeso, nAltura, nPressao, nTemperatura, dtProntuario, cHorario, nCdFuncionario, cObservacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (nCdCrianca, nPeso, nAltura, nPressao, nTemperatura, dtProntuario, horarioProntuario.strftime("%X"), nCdFuncionario, cObservacao))
        conn.commit()
    except:
        pass

    conn.close()

# Função para listar todos os dados auxiliares das crianças
def listarCriancasAux():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""SELECT *
                        FROM tbProntuario
                       INNER JOIN tbCrianca ON tbCrianca.nCdCrianca = tbProntuario.nCdCrianca""")
    criancas = cursor.fetchall()
    conn.close()

    return criancas

def listarCriancasEmail(nCdCrianca):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"""SELECT tbCrianca.cNomeCrianca
                           , strftime('%d/%m/%Y', tbCrianca.dtNascimento) as dtNascimento
                           , tbMae.cNomeMae
                           , strftime('%d/%m/%Y', tbMae.dtNascimento) as dtNascimento
                           , tbMae.cEmail
                           , tbMaeAux.cEmailContato
                           , tbFuncionario.cNomeFuncionario
                           , tbFuncionario.cEmail
                           , tbFuncionario.cEspecialidade
                       FROM tbCrianca
                       LEFT JOIN tbMae ON tbMae.nCdMae = tbCrianca.nCdMae
                       LEFT JOIN tbMaeAux ON tbMaeAux.nCdMae = tbMae.nCdMae
                       LEFT JOIN tbFuncionario ON tbFuncionario.nCdFuncionario = tbMaeAux.nCdFuncionario
                            WHERE tbCrianca.nCdCrianca = {nCdCrianca}""")
    criancas = cursor.fetchall()
    conn.close()

    return criancas

def listarProntuario(nCdProntuario):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"""SELECT *
                            , strftime('%d/%m/%Y', tbCrianca.dtNascimento) as dtNascimento
                         FROM tbProntuario
                   INNER JOIN tbCrianca ON tbCrianca.nCdCrianca = tbProntuario.nCdCrianca
                   INNER JOIN tbFuncionario ON tbFuncionario.nCdFuncionario = tbProntuario.nCdFuncionario
                        WHERE nCdProntuario = {nCdProntuario}""")
    criancas = cursor.fetchall()
    conn.close()

    return criancas

if not os.path.exists(DB_PATH):
    criar_tabelas()