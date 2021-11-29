from telegram.ext import *
from telegram import *
import requests
import re
import json
import time
import os


PORT = int(os.environ.get('PORT', 5000))
app_id = os.environ.get('APP_ID)
app_key = os.environ.get('APP_KEY')              


result = """"""


def get_sense(word_id):
    """returns the sense, word category and audio url of the given word"""

    word = word_id
    
    # REQUIREMENTS FOR THE API
    
    language = 'en-gb'
    url = 'https://od-api.oxforddictionaries.com/api/v2/entries/'  + language + '/'  + word.lower()
    r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key}).json()

    # whenever a word is misspelled or not found it returns a json response with only error in it
    # this checks and return a response if a word is either misspelled or not found
    if 'error' in r:
        return 'No entry found matching supplied word'

    # extracts the 'enteries' object from the JSON response of the API
    resp =  r['results'][0]['lexicalEntries'][0]['entries'][0]

    # extracts the senses and catagories from the 'enteries'
    sense = r['results'][0]['lexicalEntries'][0]['entries'][0]['senses']
    category = r['results'][0]['lexicalEntries'][0]['lexicalCategory']['text']

    # checks to see if an audio file is in the JSON response of the API 
    # if found it returns it with sense and category else only returns the two
    return [sense, category]


def get_audio(word):

    language = 'en-gb'
    url = 'https://od-api.oxforddictionaries.com/api/v2/entries/'  + language + '/'  + word.lower()
    r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key}).json()

    # extracts the 'enteries' object from the JSON response of the API
    resp =  r['results'][0]['lexicalEntries'][0]['entries'][0]

    if 'pronunciations' in resp:
        audio = r['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][0]['audioFile']
        return audio

    else:
        return "no audio"


def format_response(sense):
    """return dictionary object of only the needed and relevant data for the bot.
    relevant data refers to multiple definitions of the word and examples for each definition, its synonyms and audio file for pronunciation.
     It takes the raw data from the OXFORD API and only sends the relevant ones to the set_query function"""

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


def start(update, context):
    """A reply function for the command \start"""
    bot = context.bot
    bot.send_message(chat_id = update.effective_user.id,
                    text = "Give me a word so I can look it up for you")


def button(update, context):
        bot = context.bot
        # gets the keyboard callbackquery data
        query = update.callback_query
        query.answer()

        # making sure it is not the counter keyboard as its callbackquerydata is empty string
        if query.data != " ":
            # split by spaces to get the word and the id of the user
            value = query.data.split(" ")
            word = value[0]

            # request the audio for the given word
            audio_url = get_audio(word)
            
            if audio_url == 'no audio':
                bot.send_message(
                    chat_id = update.effective_chat.id,
                    text = "Sorry couldn't find the audio "
                )
            else:
                bot.send_audio(
                    chat_id = update.effective_chat.id ,
                    audio = audio_url
                )


def set_query(update: Update, context: CallbackContext):
    bot = context.bot
    query = str(update.message.text)
    userid = update.message.chat_id
    resp = get_sense(query)

    # checks to see if the response is str 
    # i.e it returns only string message when it encounters error
    # sends the error message
    if type(resp) == str:
        def send_defs(update: Update, context: CallbackContext):
                bot.send_message(
                    chat_id = userid,
                    text = resp              
                                    )
        return send_defs(Update, CallbackContext)
        
    # gets the sense, category and audio if it exists
    sense = resp[0]
    category = resp[1]
    # loops over for each object of the sense array
    # and gets its definition,examples and synonyms
    for i in range(len(sense)):
        global result
        result = """"""

        # current object of the sense array
        r = format_response(sense[i])

        definitions = r['definitions']
        examples = r['examples']
        short_definitons = r['shortDefinitions']
        non_formatted_synonyms = r['synonyms'] if r['synonyms'] else None

        # creating a keyboard so that the user can see how many varied response it got
        # and its corresponding number
        counter_keyboard = [InlineKeyboardButton(f"{i+1}",callback_data=" ")]

        #creating a keyboard so the user can request an audio file for the word
        audio_keyboard = [InlineKeyboardButton("Get Audio",callback_data=f"{query} {userid}")]


        # a function that sends the defn, examples and the synonyms
        def send(text,i):

            # checks to see if it is the end of loop so we can add the 'GET AUDIO' keyboard together with the message
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
            """converts the synoyms of the given word to strings so it be attached to message template"""
            synonyms = """"""
            if li:
                for i in li:
                    if type(i) == dict:
                        for key, value in i.items():
                            if key == 'text':
                                synonyms+= i['text'] + ", \t"
            return synonyms


        def join_them(defns="", exs="",syns=""):
            """updates the result variable by joining the defs, examples and synonyms to the MESSSGE TEMPLATE """
            global result

            # the message Template
            result += """
𝙒𝙤𝙧𝙙: {}

𝘾𝙖𝙩𝙚𝙜𝙤𝙧𝙮: {}

𝘿𝙚𝙛𝙞𝙣𝙞𝙩𝙞𝙤𝙣: {}

𝙀𝙭𝙖𝙢𝙥𝙡𝙚𝙨: {}

𝙎𝙮𝙣𝙤𝙣𝙮𝙢𝙨: {}""".format(query, category, defns[0] if type(exs) is list else "" , exs[0] if type(exs) is list else "", syns)
# for the above string formatting, the if else is to check 
# wether the given word has the defs,examples or syns if not just append empty string


        # checks if the parameters are empty or not, if they are empty just call the fun(no params)
        def check_and_send(defs,exs,syns):
            if len(defs) > 0 and len(exs) > 0:
                join_them(defs,exs,syns)
            else:
                join_them()
        
        
        # converts the dictionary obj to comma separated strings 
        formatted_synonyms = format_synonyms(non_formatted_synonyms)
        # updates the result variable
        check_and_send(definitions,examples,formatted_synonyms)
        # sends the result variable along with the current loop number
        send(result,i)
        time.sleep(.5)



def main():
    TOKEN = "1597724996:AAGKQD_U8Dhsuh_TmUYGfZotIzHsF5n41mk"
    bot = Bot(TOKEN)
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, set_query,run_async=True))
    dp.add_handler(CallbackQueryHandler(button,run_async=True))


    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://engdictionarybot.herokuapp.com/' + TOKEN)



if __name__ == '__main__':
    main()

