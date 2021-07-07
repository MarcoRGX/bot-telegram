import logging
import telegram
import requests
from bs4 import BeautifulSoup
from telegram.ext import CommandHandler,MessageHandler,Filters,Updater
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator, authenticator

def dolar():
    url = 'https://coinyep.com/es/ex/USD-MXN'
    pagina = requests.get(url)
    bs = BeautifulSoup(pagina.content, 'html.parser')

    mensajes = bs.find_all('small', {'id': 'coinyep-reverse1'})
    texto = open('mensajes.txt', 'w')

    for i in mensajes:
        texto.write(i.text)
    texto.close()

    msm = open('mensajes.txt')
    mensajes = []

    for i in msm:
        if i != '/n':
            mensajes.append(i)
    return mensajes[0]

def oferta():
    url = requests.get("https://www.mercadolibre.com.mx/amazon-echo-dot-3rd-gen-con-asistente-virtual-alexa-charcoal-110v240v/p/MLM15534261?pdp_filters=category:MLM187752#searchVariation=MLM15534261&position=1&search_layout=stack&type=product&tracking_id=778086f2-f942-4d0a-9e2d-a9ef9db7655f")
    soup = BeautifulSoup(url.content, "html.parser")
    resultado = soup.find("span", {"class":"price-tag-fraction"})
    precioInicio_text = resultado.text

    #Convertimos el valor que obtenemos
    precioInicial = float(precioInicio_text)
    print(precioInicial)
    precioDeseado = 1000

    if precioInicial < precioDeseado:
        return ("Genial tu producto esta en oferta: \n"+"https://n9.cl/elbuky")
    else:
        return ("Lo siento tu producto aun tiene un precio mayor")

class Chatbot:
    def __init__(self, token='1771120161:AAH7uRAvRAtmZK5yk_T-hitZXBDpovH7RTM'):#Token de Telegram

        self.updater = Updater(token=token,use_context=True)
        self.dispatcher = self.updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s %(levelname)s - %(message)s',level=logging.INFO)
        authenticator= IAMAuthenticator('U49NlfBstSgo-odWTjCJJ6yY6_Jjg-pYhSvuZ7Y8iwnp') #Token de IBM Watson
        self.speech2text = SpeechToTextV1(authenticator)

        self.hola_handler = CommandHandler('Hola',self.hola)
        self.dispatcher.add_handler(self.hola_handler)


        self.bot = telegram.Bot(token=token)
        self.obtener_audio= MessageHandler(Filters.voice,self.guardar_audio)
        self.dispatcher.add_handler(self.obtener_audio)

        self.obtener_text= MessageHandler(Filters.text,self.texto)
        self.dispatcher.add_handler(self.obtener_text)

        self.updater.start_polling()
        self.updater.idle()


    def guardar_audio(self, update,context):
        print('Entrada de audio')
        archivo = self.bot.getFile(update.message.voice.file_id)
        archivo.download('mensaje_audio.ogg')
        audio =open('mensaje_audio.ogg','rb')
        res = self.speech2text.recognize(audio=audio,content_type='audio/ogg',timestamps=True,model='es-MX_BroadbandModel',word_confidence=True)
        lista = res.get_result()['results'][0]['alternatives'][0]['timestamps']
        persona =update.message.from_user
        for datos in lista:
            print(datos[0],'Precision de: ',datos[1])
        
            if datos[0]=='hola' or datos[0]=='comenzar' or datos[0]=='saludos' or datos[0]=='volver' or datos[0]=='buenas' or datos[0]=='menu':
                context.bot.send_message(chat_id=update.effective_chat.id,text='Elige la opcion que necesites utilizar'+ '\n'+ '1.- Precio del dolar'+ '\n'+'2.- Consultar oferta')
                context.bot.send_sticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAEB27ZgIDJ9W9gIC6hYDew72x2LMu-yIwAC2AEAAladvQqY1H8pZ85AOR4E')

            if datos[0]=='uno':
                #Llamamos a la funcion dolar para consultar el precio del dolar
                print(dolar())
                context.bot.send_message(chat_id=update.effective_chat.id,text='Precio del dolar'+'\n'+ dolar())
                context.bot.send_sticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAECghZg27kpX9zJcUEdPgq6zv7Djbjs9AAC8QEAAladvQohKm5i6iYv7iAE')

            if datos[0]=='dos':
                #Llamamos a la funcion oferta para consultar el precio del producto y con el evaluar si esta por debajo del precio deseado
                context.bot.send_message(chat_id=update.effective_chat.id,text='Consultar oferta'+'\n'+oferta())         
                context.bot.send_sticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAECghhg27zvwtjcYC7fHH9_EriUmc9bqwAClwMAAkcVaAl7ulQ5f-kIUiAE')
            
            if datos[0] != "hola" and datos[0] != "uno" and datos[0]!= "dos" and datos[0] != "menu":
                context.bot.send_message(chat_id=update.effective_chat.id,text='Disculpa no te entendi'+'\n'+'😢')
                context.bot.send_message(chat_id=update.effective_chat.id,text='Elige la opcion que desee utilizar'+ '\n'+ '1.- Precio del dolar'+ '\n'+'2.- Consultar oferta')
                context.bot.send_sticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAEB27ZgIDJ9W9gIC6hYDew72x2LMu-yIwAC2AEAAladvQqY1H8pZ85AOR4E')

    def texto(self,update,context):
        print('Entrada de Texto')
        text_mensaje= update.message.text
        mensaje = text_mensaje.title()
        mensaje2 = text_mensaje.title()
        persona =update.message.from_user
        print(mensaje)
        if mensaje=="/Start":
                context.bot.send_message(chat_id=update.effective_chat.id,text='Hola, '+ persona['first_name']+'\n'+'Soy tu asistente virtual Monitor Tesji 🥰'+'\n'+'Cuando estes listo escribe Comenzar')  
                context.bot.send_sticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAEB27ZgIDJ9W9gIC6hYDew72x2LMu-yIwAC2AEAAladvQqY1H8pZ85AOR4E')
            
        if mensaje=='Hola' or mensaje =='Comenzar' or mensaje=='Saludos' or mensaje=='Volver' or mensaje =='Buenas' or mensaje=='👋' or mensaje=='Menu' or mensaje=='Gracias':
                context.bot.send_message(chat_id=update.effective_chat.id,text='Elige la opcion que necesitas utilizar'+ '\n'+ '1.- Precio del dolar'+ '\n'+'2.- Consultar oferta')
                context.bot.send_sticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAEB27ZgIDJ9W9gIC6hYDew72x2LMu-yIwAC2AEAAladvQqY1H8pZ85AOR4E')

        if mensaje=='1' or mensaje =='Uno':
            #Llamamos a la funcion dolar para consultar el precio del dolar
            print(dolar())
            context.bot.send_message(chat_id=update.effective_chat.id,text='Precio del dolar'+'\n'+ dolar())
            context.bot.send_sticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAECghZg27kpX9zJcUEdPgq6zv7Djbjs9AAC8QEAAladvQohKm5i6iYv7iAE')

        elif mensaje=='2' or mensaje =='Dos':
            #Llamamos a la funcion oferta para consultar el precio del producto y con el evaluar si esta por debajo del precio deseado
                context.bot.send_message(chat_id=update.effective_chat.id,text='Consultar oferta'+'\n'+oferta())         
                context.bot.send_sticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAECghhg27zvwtjcYC7fHH9_EriUmc9bqwAClwMAAkcVaAl7ulQ5f-kIUiAE')

        if mensaje != "1" and mensaje != "2" and mensaje!= "Uno" and mensaje!= "Dos" and mensaje != "Hola" and mensaje != "Comenzar" and mensaje != "Gracias" and mensaje != "/Start" and mensaje != "Volver" and mensaje != "👋":
            context.bot.send_message(chat_id=update.effective_chat.id,text='Disculpa no te entendi'+'\n'+'😢')
            context.bot.send_message(chat_id=update.effective_chat.id,text='Elige la opcion que necesitas utilizar'+ '\n'+ '1.- Precio del dolar'+ '\n'+'2.- Consultar oferta')
            context.bot.send_sticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAEB27ZgIDJ9W9gIC6hYDew72x2LMu-yIwAC2AEAAladvQqY1H8pZ85AOR4E')


    def hola(self,update,context):
        print('comando hola')
        persona =update.message.from_user
        context.bot.send_message(chat_id=update.effective_chat.id,text='hola, ' + persona['first_name']+'Soy tu asistente virtual ') 
 
if __name__ == '__main__':
    chatbot = Chatbot()
