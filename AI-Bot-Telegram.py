import telebot
import whisper
import requests
import openai
import asyncio
from dotenv import load_dotenv
import os


load_dotenv('E:\КУРСЫ Python-разработчик\Чат-бот\secret.env')

openai.api_key = os.getenv('OPENAI_API_KEY')
token = os.getenv('TG_API_TOKEN')
bot = telebot.TeleBot(token, parse_mode=None)


@bot.message_handler(content_types=['voice', 'text'])
def repeat_all_message(message):
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))

    with open('voice.mp3', 'wb') as f:
        f.write(file.content)
        f.close()
        text_reco(message)
    # Функция сохранения гс


async def question_to_answer(prompt):
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()
    # Функция ответа на вопрос


async def main(question):
    answer = await question_to_answer(question)
    print(f"Ответ: {answer}")
    text_to_speech(answer, "output.mp3")


def text_reco(message):
    model = whisper.load_model("small")
    audio = whisper.load_audio('./voice.mp3')
    audio = whisper.pad_or_trim(audio)
    result = model.transcribe(audio)
    print(result['text'])
    bot.reply_to(message, f"Ты сказал мне: {result['text']}")
    asyncio.run(main(result['text']))
    # Функцуия распознавание текста


def text_to_speech(text, output_file):
    response = await openai.Audio.create(
        model="audio.speech.create",
        text=text,
        voice="ru-RU"
    )
    with open(output_file, "wb") as out:
        out.write(response['audio_content'])
        print(f"Аудио готово вот: {output_file}")
    # Функция озвучки полученых ответов


if __name__ == '__main__':
    bot.polling(none_stop=True)
