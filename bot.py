from telegram.ext import *
from telegram import *
import requests
import re
import json
import time


# TODO
# WORK ON SYNOMYMS AND ANTONYMS || DONE
# TO SEND THE DEFINITION , EXAMPLES AND SYNONYMS TOGETHER AS ONE MESSAGE || DONE
# ERROR HANDLING FOR MISPELLED WORDS  || DONE
# Write documentation || IM FUCKED ON THAT
# BUTTON THAT acts as a tera kutir || DONE
# ADD A BUTTON THAT GIVES AUDIO FOR PRONOUNCIATION || DONE
# hyperlink in each synoyms and when clicked it brings the definitions of that word || KINDA A LOT OF WORK FOR USELESS BOT
# INLINE FEATURES || DEFINITELY GONNA TRY IT OUT


def get_sense(word_id):
    word = word_id
    app_id = '614936c6'
    app_key = 'e4766346cf2fc5e4a55f254c8e96e9bf'
    language = 'en-gb'
    url = 'https://od-api.oxforddictionaries.com/api/v2/entries/'  + language + '/'  + word.lower()
    r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key}).json()
    if 'error' in r:
        return 'No entry found matching supplied word'
    resp =  r['results'][0]['lexicalEntries'][0]['entries'][0]
    sense = r['results'][0]['lexicalEntries'][0]['entries'][0]['senses']
    category = r['results'][0]['lexicalEntries'][0]['lexicalCategory']['text']

    if 'pronunciations' in resp:
        audio = r['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][0]['audioFile']
        return [sense, category, audio]
    return [sense, category]


def format_response(sense):
    definitions = []
    examples_dics = []
    examples = []
    short_definitons = []
    synonyms = []


    def loop_over(li,key):
        if key in sense:
            for i in sense[key]:
                li.append(i)
            return li
        else:
            return None

    loop_over(definitions,'definitions')
    loop_over(examples_dics,'examples')
    loop_over(short_definitons,'shortDefinitions')
    loop_over(synonyms,'synonyms')

    for dic in examples_dics:
        for key,value in dic.items():
            if key == 'text':
                examples.append(value)

    return {'definitions':definitions, 'examples': examples, 'shortDefinitions': short_definitons, 'synonyms': synonyms }



result = """"""
audio = ""


def main():
    TOKEN = "1597724996:AAGKQD_U8Dhsuh_TmUYGfZotIzHsF5n41mk"
    bot = Bot(TOKEN)
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher


    def start(update, context):

        bot.send_message(chat_id = update.effective_user.id,
                         text = "Give me a word so I can look it up for you")


    def set_query(update: Update, context: CallbackContext):
        
        query = str(update.message.text)
        userid = update.effective_chat.id
        resp = get_sense(query)
        
        if type(resp) == str:
            def send_defs(update: Update, context: CallbackContext):
                    bot.send_message(
                        chat_id = userid,
                        text = resp              
                                    )
            return send_defs(Update, CallbackContext)
        

        sense = resp[0]
        category = resp[1]

        if len(resp) >2:
            global audio
            audio = resp[2]

        for i in range(len(sense)):
            global result
            result = """"""
            r = format_response(sense[i])

            definitions = r['definitions']
            examples = r['examples']
            short_definitons = r['shortDefinitions']
            non_formatted_synonyms = r['synonyms'] if r['synonyms'] else None

            counter_keyboard = [InlineKeyboardButton(f"{i+1}",callback_data="just a button")]
            audio_keyboard = [InlineKeyboardButton("Get Audio",callback_data="audio")]


            def send(text,i):
                if i+1 != len(sense):
                    reply_markup = InlineKeyboardMarkup([counter_keyboard])
                    def send_defs(update: Update, context: CallbackContext):
                        bot.send_message(
                            chat_id = userid,
                            text = text,
                            reply_markup=reply_markup              
                                        )

                else:
                    reply_markup = InlineKeyboardMarkup([counter_keyboard,audio_keyboard])
                    def send_defs(update: Update, context: CallbackContext):
                        bot.send_message(
                            chat_id = userid,
                            text = text,
                            reply_markup=reply_markup              
                                        )
                return send_defs(Update, CallbackContext)

                
            def format_synonyms(li):
                synonyms = """"""
                if li:
                    for i in li:
                        if type(i) == dict:
                            for key, value in i.items():
                                if key == 'text':
                                    synonyms+= i['text'] + ", \t"
                return synonyms


            def join_them(defns="", exs="",syns=""):
                global result
                result += """
𝙒𝙤𝙧𝙙: {}

𝘾𝙖𝙩𝙚𝙜𝙤𝙧𝙮: {}

𝘿𝙚𝙛𝙞𝙣𝙞𝙩𝙞𝙤𝙣: {}

𝙀𝙭𝙖𝙢𝙥𝙡𝙚𝙨: {}

𝙎𝙮𝙣𝙤𝙣𝙮𝙢𝙨: {}""".format(query, category, defns[0] if type(exs) is list else "" , exs[0] if type(exs) is list else "", syns)
                                        

            def check_and_send(defs,exs,syns):
                if len(defs) > 0 and len(exs) > 0:
                    join_them(defs,exs,syns)
                else:
                    join_them()
            
                
            formatted_synonyms = format_synonyms(non_formatted_synonyms)
            check_and_send(definitions,examples,formatted_synonyms)
            send(result,i)
            time.sleep(.5)


        def send_audio(update: Update, context: CallbackContext):
            bot.send_audio(
                    chat_id = userid,
                    audio = audio,
                    filename = f"{query}",
                    caption = f"Pronunciation for the word '{query}'"             
                            )  
                            
                             
        def button(update: Update, context: CallbackContext) -> None:
            query = update.callback_query
            query.answer()
            value = query.data

            if value == 'audio':
                if len(resp) >2:
                    send_audio(Update, CallbackContext)


        updater.dispatcher.add_handler(CallbackQueryHandler(button))

    
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, set_query))
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://engdictionarybot.herokuapp.com/' + TOKEN)

    
if __name__ == '__main__':
    main()