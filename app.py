from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, get_flashed_messages
from flask_mail import Mail, Message
import string, random, os
from liteDatabase.conexaoSQL import *

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app = Flask(__name__)

app.secret_key = '??????'

def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/')
def index():
    return render_template('paginalogin.html')

@app.route('/login', methods=['POST'])
def login():
    cLoginEmail = request.form['cLoginEmail']
    cSenha = request.form['cSenha']

    user = validaLoginFuncionario(cLoginEmail)

    if user and bcrypt.checkpw(cSenha.encode('utf-8'), user[3].encode('utf-8')):
        session['logged_in'] = True
        session['user_id'] = user[0]
        return redirect(url_for('prontuario'))
    else:
        flash('A senha e a confirmação de senha não correspondem.', 'error')
        return redirect(url_for('paginalogin'))


@app.route('/paginalogin')
def paginalogin():    
    return render_template('paginalogin.html')

@app.route('/prontuario')
def prontuario():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        user = dadosFuncionarioLogado(user_id)


        maesCadastradas = listarMaesAux()

        criancasCadastradas = listarCriancas()

        prontuariosCadastrados = listarCriancasAux()

        return render_template('prontuario.html', user=user, maesCadastradas=maesCadastradas, criancasCadastradas=criancasCadastradas, prontuariosCadastrados=prontuariosCadastrados)
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/addMae', methods=['POST'])
def addMae():
    if 'logged_in' in session and session['logged_in']:
        cNomeMae = request.form['cNomeMae']
        cCPF = request.form['cCPF']
        dtNascimento = request.form['dtNascimento']
        cEndereco = request.form['cEndereco']
        cNumero = request.form['cNumero']
        cEmail = request.form['cEmail']

        cadastrarMae(cNomeMae, cCPF, dtNascimento, cEndereco, cNumero, cEmail)

        nCdMae = listarMaesBase(cNomeMae, cCPF)

        cadastrarMaeAuxBase(nCdMae)
    
        flash(f'A mãe {cNomeMae} foi cadastrada com sucesso!.', 'success')
        return redirect(url_for('prontuario'))

@app.route('/editarCadastroMae/<int:nCdMae>')
def editarCadastroMae(nCdMae):
    dadosBase = listarMaes(nCdMae)
    dadosAux = listarMaesAuxi(nCdMae)
    funcionariosCadastrados = listarFuncionarios()
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        user = dadosFuncionarioLogado(user_id)

        if request.method == 'POST':
            cEndereco = request.form['cEndereco']
            cNumero = request.form['cNumero']
            cEmail = request.form['cEmail']
            cEmailContato = request.form['cEmailContato']
            nCdFuncionario = request.form['nCdFuncionario']

            atualizarMae(nCdMae, cEndereco, cNumero, cEmail)

            if dadosAux:
                atualizarMaeAux(nCdMae, nCdFuncionario, cEmailContato)
            else:
                cadastrarMaeAux(nCdMae, nCdFuncionario, cEmailContato)

            flash(f'Dados atualizados com sucesso com sucesso!.', 'success')

            return redirect(url_for('perfil'))

        return render_template('editarCadastroMae.html', user=user, dadosBase=dadosBase, dadosAux=dadosAux, nCdMae=nCdMae, funcionariosCadastrados=funcionariosCadastrados)
    else:
        return redirect(url_for('index'))

@app.route('/salvarCadastroMae', methods=['POST'])
def salvarCadastroMae():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        user = dadosFuncionarioLogado(user_id)
        nCdMae = request.form['nCdMae']
        cNomeMae = request.form['cNomeMae']
        cEndereco = request.form['cEndereco']
        cNumero = request.form['cNumero']
        cEmail = request.form['cEmail']
        cEmailContato = request.form['cEmailContato']
        nCdFuncionario = request.form['nCdFuncionario']

        dadosAux = listarMaesAuxi(nCdMae)   

        atualizarMae(nCdMae, cEndereco, cNumero, cEmail)

        if dadosAux:
            atualizarMaeAux(nCdMae, nCdFuncionario, cEmailContato)
        else:
            cadastrarMaeAux(nCdMae, nCdFuncionario, cEmailContato)

        flash(f'Dados da mãe {cNomeMae} atualizados com sucesso!.', 'success')

        return redirect(url_for('prontuario'))
    else:
        return redirect(url_for('index'))

@app.route('/addCrianca', methods=['POST'])
def addCrianca():
    if 'logged_in' in session and session['logged_in']:
        cNomeCrianca = request.form['cNomeCrianca']
        dtNascimento = request.form['dtNascimento']
        nCdMae = request.form['nCdMae']

        cadastrarCrianca(cNomeCrianca, dtNascimento, nCdMae)
    
        flash(f'A criança {cNomeCrianca} foi cadastrada com sucesso!.', 'success')
        return redirect(url_for('prontuario'))

@app.route('/addProntuario', methods=['POST'])
def addProntuario():
    if 'logged_in' in session and session['logged_in']:
        nCdFuncionario = session['user_id']
        nCdCrianca = request.form['nCdCrianca']
        nPeso = request.form['nPeso']
        nPeso = nPeso.replace(".",",")
        nAltura = request.form['nAltura']
        nAltura = nAltura.replace(".",",")
        nPressao = request.form['nPressao']
        nPressao = nPressao.replace(".",",")
        nTemperatura = request.form['nTemperatura']
        nTemperatura = nTemperatura.replace(".",",")
        dtProntuario = request.form['dtProntuario']
        cObservacao = request.form['cObservacao']

        cadastrarCriancaAux(nCdCrianca, nPeso, nAltura, nPressao, nTemperatura, dtProntuario, nCdFuncionario, cObservacao)
        enviarEmailProntuario(nCdCrianca, nPeso, nAltura, nPressao, nTemperatura, dtProntuario, nCdFuncionario, cObservacao)
        
    flash('Prontuário salva com sucesso!.', 'success')
    return redirect(url_for('prontuario'))

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        cNomeFuncionario = request.form['cNomeFuncionario']
        cEmail = request.form['cEmail']
        cEspecialidade = request.form['cEspecialidade']
        cLogin = request.form['cLogin']
        cSenha = request.form['cSenha']
        cConfirmarSenha = request.form['cConfirmarSenha']

        if cSenha != cConfirmarSenha:
            flash('A senha e a confirmação de senha não coincidem. Por favor, tente novamente.', 'error')
            return redirect(url_for('cadastrar'))

        
        try:
            cadastrarFuncionario(cNomeFuncionario, cEspecialidade, cEmail, cLogin, cSenha)
            enviarEmailCadastro(cEmail, cNomeFuncionario, cEspecialidade, cLogin, cSenha)
            flash('Usuário registrado com sucesso! Os dados de acesso foram enviados para o e-mail informado', 'success')
            return redirect(url_for('index'))
        except:
            flash('Erro ao cadastrar o usuário, tente novamente ou entre em contato com o suporte!', 'error')
            return redirect(url_for('index'))

    return render_template('cadastrar.html')

def enviarEmailCadastro(cEmail, cNomeFuncionario, cEspecialidade, cLogin, cSenha):
    mail = Mail(app)

    app.config['MAIL_SERVER'] = "smtp.gmail.com"
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    mail.init_app(app)

    loginLink = f'http://127.0.0.1:5002'

    msg = Message('Assunto do E-mail', sender='suportelhrp@gmail.com', recipients=[cEmail])

    msg.body = f'''
    Olá,

    Você foi cadastrado no sistema da Matrelife!
    Seguem abaixo, os seus dados cadastrados:

    Nome: {cNomeFuncionario}
    Especialidade: {cEspecialidade}
    Login: {cLogin}
    E-mail: {cEmail}
    Senha: {cSenha}
    
    Clique no link abaixo para acessar sua conta:
    {loginLink}

    Obrigado!
    '''
    mail.send(msg)

def enviarEmailProntuario(nCdCrianca, nPeso, nAltura, nPressao, nTemperatura, dtProntuario, nCdFuncionario, cObservacao):

    dadosCrianca = listarCriancasEmail(nCdCrianca)

    destinatarios = []

    cNomeCrianca = dadosCrianca[0][0]
    dtNascimento = dadosCrianca[0][1]
    cNomeMae = dadosCrianca[0][2]
    dtNascimentoMae = dadosCrianca[0][3]
    cNomeFuncionario = dadosCrianca[0][6]
    cEmailMae = dadosCrianca[0][4]
    cEmailContato = dadosCrianca[0][5]
    cEmailFuncionarioResponsavel = dadosCrianca[0][7]
    cEspecialidade = dadosCrianca[0][8]

    if cNomeFuncionario == None:
        cNomeFuncionario = 'Não Definido'
    if cEspecialidade == None:
        cEspecialidade = 'Não Definido'

    if cEmailMae != None and cEmailMae != 'Não Informado':
        destinatarios.append(cEmailMae)
    if cEmailContato != None and cEmailContato != 'Não Informado':
        destinatarios.append(cEmailContato)
    if cEmailFuncionarioResponsavel != None and cEmailFuncionarioResponsavel != 'Não Informado':
        destinatarios.append(cEmailFuncionarioResponsavel)

    mail = Mail(app)

    app.config['MAIL_SERVER'] = "smtp.gmail.com"
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    mail.init_app(app)

    msg = Message(f'Atualização do Prontuário da criança {cNomeCrianca}', sender='suportelhrp@gmail.com', recipients=destinatarios)

    msg.body = f'''
    Olá,

    Você está definido como um dos contatos a receber as atualizações do prontuário da criança {cNomeCrianca}, 
    onde acaba de ser incluso o registro abaixo no prontuário:

    Data do Prontuário: {dtProntuario}

    Nome da Criança: {cNomeCrianca}
    Data de Nascimento: {dtNascimento}

    Mãe: {cNomeMae}
    Data de Nascimento: {dtNascimentoMae}

    Responsável pelo Prontuário: {cNomeFuncionario}
    Especialidade: {cEspecialidade}

    Peso: {nPeso}
    Altura: {nAltura}
    Pressão: {nPressao}
    Temperatura: {nTemperatura}

    Observaçoes: {cObservacao}

    '''
    mail.send(msg)

@app.route('/buscarNomeCrianca/<nCdCodigoCrianca>', methods=['GET'])
def buscarNomeCrianca(nCdCodigoCrianca):

    
    try:
        nCdCrianca = buscarCriancaCodigoGerado(nCdCodigoCrianca)[0][0]
        cNomeCrianca = buscarCriancaCodigoGerado(nCdCodigoCrianca)[0][1]
    except:
        cNomeCrianca = ''

    if cNomeCrianca:
        return jsonify({'success': True, 'nCdCrianca': nCdCrianca, 'cNomeCrianca': cNomeCrianca})
    else:
        return jsonify({'success': False}), 404

@app.route('/buscasDetalhesProntuario', methods=['GET'])
def buscasDetalhesProntuario():
    idProntuario = request.args.get('id')
    user_id = session['user_id']
    
    prontuarios = listarProntuario(idProntuario)

    detalhes_tarefa = {
        'prontuarioNomeCrianca': prontuarios[0][14] + ' - ' + prontuarios[0][11],
        'prontuarioPeso': prontuarios[0][2],
        'prontuarioAltura': prontuarios[0][3],
        'prontuarioPressao': prontuarios[0][4],
        'prontuarioTemperatura': prontuarios[0][5],
        'prontuarioHorario': prontuarios[0][7],
        'prontuarioObservacao': prontuarios[0][9],
        'prontuarioNascimento': prontuarios[0][21],
        'prontuarioFuncionario': prontuarios[0][16],
        'prontuarioEspecialidade': prontuarios[0][17],
    }

    return jsonify(detalhes_tarefa)

bootstrap_css_link = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css"


@app.route('/get_flash_messages', methods=['GET'])
def get_flash_messages():
    messages = get_flashed_messages()
    return jsonify({'messages': messages})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
