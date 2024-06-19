from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
import requests
import google.generativeai as genai
import json
import re
from .models import Usuario
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse


from .models import Usuario  # Se estiver usando um modelo de usuário personalizado

def perguntas_frequentes(request):
    print('passei aqui')
    if request.method == 'GET':
        response_data = {}
        response_data['result'] = 'perguntas'
        response_data['message'] = 'Some error message'
        #return JsonResponse({'perguntas': 'flavinho do pneu'})
        return HttpResponse(json.dumps(response_data), content_type="application/json")


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not (email and password):
            # Se algum campo estiver vazio, renderize o template com um alerta
            return render(request, 'login.html', {'error_message': 'Por favor, preencha todos os campos.'})
        elif Usuario.objects.filter(email=email).exists():
            userx = Usuario.objects.filter(email=email).first()
            if userx.email == email and userx.password == password:
                auth_login(request, userx)
                return redirect(reverse('conversar'))
            else:
                return render(request, 'login.html', {'error_message': 'Senha inválida'})
        else:
            return render(request, 'login.html', {'error_message': 'Esse email não está cadastrado'})
    else:
        return render(request, 'login.html')

@login_required
def conversar(request):
    return render(request, 'chat.html')


def cadastro(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        area = request.POST.get('area')
        password = request.POST.get('password')
        if not (name and email and area and password):
            # Se algum campo estiver vazio, renderize o template com um alerta
            return render(request, 'cadastro.html', {'error_message': 'Por favor, preencha todos os campos.'})

        if Usuario.objects.filter(email=email).exists():
            # Se o usuário já existir, renderize o template com um alerta
            return render(request, 'cadastro.html', {'error_message': 'Este email já está em uso.'})

        # Se tudo estiver correto, crie o usuário e redirecione para a página de login
        usuario = Usuario()
        usuario.nome = name
        usuario.email = email
        usuario.area = area
        usuario.senha = password
        usuario.save()
        return redirect(reverse('login'))
    else:
        return render(request, 'cadastro.html')

    

def iaProcess(mensage, user_info):
    APIKEY = "Your key"

    genai.configure(api_key=APIKEY)

    model = genai.GenerativeModel('gemini-pro')
    chatFoiCriado = False
    SairDoChat = ''
    pergunta = f'''
                   A pergunta é :{mensage},
                   Assuma que você é um chatbot da empresa IWS Intelliware Soluctions,
                   Use como base para responder as peguntas as inormações presentes no site oficial da empresa,
                   Responda as perguntas de forma amigavel,
                   Você esta falando com {user_info["name"]},
                   A area de atução do usuario no mercado é: {user_info["area"]},
                   responda a perguta de forma sucinta,         
                '''
    try:
        if not chatFoiCriado:
            chat = model.start_chat()
            chatFoiCriado = True
        response = chat.send_message(pergunta)
        SairDoChat = model.generate_content(f'''Na seguinte mensagem : '{pergunta}', o usuário deseja encerrar a conversa?
                                                (responda apenas sim ou não)''').text
        mensagem_ofensiva = model.generate_content(f'''A seguinte mensagem : '{pergunta}', é uma mensagem ofenciva?
                                                (responda apenas sim ou não)''').text
        if SairDoChat == 'Sim':
            if mensagem_ofensiva == 'Sim':
                return 'Por favor, evite mensagens ofensivas'
            else:
                return 'Espero ter ajudado.'
        try:
            resposta = response.text
            return resposta
        except Exception as e:
                semResposta = 'Não fui capaz de gerar uma resposta, por favor, faça a pergunta novamente'
                return semResposta
    except Exception as e:
        listaDeViolações = ''
        contadorDeViolções = 0
        regexJson = re.compile(r'safety_ratings \{.*?\}', re.DOTALL)
        correspondencias = regexJson.findall(str(e))
        for correspondencia in correspondencias:
            correspondencia_corrigida = re.sub(r'(\w+):', r'"\1":', correspondencia[len('safety_ratings '):-1])
            correspondencia_corrigida = re.sub(r':\s(\w+)', r':"\1"', correspondencia_corrigida)
            correspondencia_corrigida = re.sub(r'("category":".*"?)', r'\1,', correspondencia_corrigida)
            jsonDeViolação = json.loads(correspondencia_corrigida + '}')
            if jsonDeViolação.get('probability') == 'HIGH':
                regexErro =  jsonDeViolação.get('category').replace('HARM_CATEGORY_', '')
                regexErro =  regexErro.replace('_', ' ')
                if contadorDeViolções == 0:
                    listaDeViolações += regexErro
                    contadorDeViolções += 1 
                elif contadorDeViolções != 0:
                    regexErro = ', ' + regexErro
                    listaDeViolações += regexErro
        if len(listaDeViolações) == 0:
            return 'Sua pergunta foi bloqueada'
        else:
            saidaErro = 'Sua pergunta foi bloqueada por vilolar o(s) seguinte(s) termo(s): ' +'"'+ listaDeViolações + '"'
        return saidaErro
    
@login_required
def process_message(request):
    if request.method == 'GET':
        message = request.GET.get('usermessage')
        user = request.user  # Isso assume que você está usando o sistema de autenticação do Django

        # Exemplo de como enviar informações do usuário para iaProcess
        user_info = {
            'name': user.nome,
            'email': user.email,
            'area': user.area,
        }
        print(user_info)
        # Envie a mensagem para a função iaProcess com as informações do usuário
        response = iaProcess(message, user_info)

        return HttpResponse(response)
    else:
        return HttpResponse('Método não permitido', status=405)


def send_to_dialogflow(message):
    dialogflow_language_code = 'pt-BR'
    headers = {'Content-Type': 'application/json'}
    data = {'queryInput': {'text': {'text': message, 'languageCode': dialogflow_language_code}}}
    
    response = requests.post(
        'YOUR_DIALOGFLOW_API_ENDPOINT',
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json().get('queryResult').get('fulfillmentText')
    else:
        return 'Desculpe, ocorreu um erro ao processar sua solicitação.'