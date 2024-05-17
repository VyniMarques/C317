from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
import google.generativeai as genai
import json
import re
from .models import Usuario

def conversar(request):
    return render(request, 'chat.html')


def login(request):
    return render(request, 'login.html')

def cadastro(request):
    print(request.POST.get('email') == '')
    if request.POST.get('name') == None and request.POST.get('email') == None and request.POST.get('area') == None and request.POST.get('password') == None :
        print('palmeiras')
        return render(request, 'cadastro.html')
    elif request.POST.get('name') == '' or request.POST.get('email') == '' or request.POST.get('area') == '' or request.POST.get('password') == '' :
        print('flamengo')
        return render(request, 'cadastro.html')
    else:
        if Usuario.objects.filter(email=request.POST.get('email')).exists():
            print('corinthans')
            return render(request, 'cadastro.html')
        else:
            print('cruzeiro')
            usuario = Usuario()
            usuario.nome = request.POST.get('name')
            usuario.email = request.POST.get('email')
            usuario.area = request.POST.get('area')
            usuario.senha = request.POST.get('password')
            #usuario.save()
            render(request,'login.html')

    

def iaProcess(mensage):
    APIKEY = 'API key'

    genai.configure(api_key=APIKEY)

    model = genai.GenerativeModel('gemini-pro')
    chatFoiCriado = False
    SairDoChat = ''
    pergunta = mensage
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
    
def process_message(request):
    message = request.GET.get('usermessage')   
    # Envie a mensagem para o serviço de IA (por exemplo, Dialogflow)
    response = iaProcess(message)
    return HttpResponse(response)


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
        print(response.status_code)
        return 'Desculpe, ocorreu um erro ao processar sua solicitação.'