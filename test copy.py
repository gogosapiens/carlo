from carlo import printc
from carlo import gpt

# def validate_resp(response):
#     # print("validating response", response)
#     response['title'] = "value1"
#     return True
    
# def optimizer_resp(response):
#     # print("optimizing response", response)
#     # if isinstance(response, str):
#     #     return "value222"
#     # else:
#     return 1

import time
times = []
desired_answers = [
    {
        "note":"Tone: Calm",
        "answer_id":"0",
        "words_count_max":15,
        "words_count_min":5
    },
    {
        "words_count_min":5,
        "words_count_max":15,
        "note":"Tone: Calm",
        "answer_id":"1"
    },
    {
        "note":"Tone: Calm",
        "answer_id":"2",
        "words_count_min":5,
        "words_count_max":15
    }
]
comments = [
    {
        "author":"@b_a_s_999",
        "text":"Досмотрел ☺️ кайфанул, зарядился творчески, обомлел от шикарного заката над Стоунхендж, и восхитился архитектурой Оксфорда🤩 спасибо за новый фильм, жду выпуск из Лондона. Всем мир ✌🏽️",
        "comment_id":"UgzcswCq-mjiQjUNMNJ4AaABAg"
    },
    {
        "author":"@Elena-qt8cc",
        "comment_id":"UgzVA3rHLLNtIFtIT9R4AaABAg",
        "text":"Ребята, огромная благодарность. 🙏\nВаши фильмы - всегда как праздник выходного дня."
    },
    {
        "comment_id":"UgxYSaKGJ4qqDOjvqkR4AaABAg",
        "author":"@about.a.girl.toryvi",
        "text":"Невероятно красиво! Спасибо, что у нас есть возможность путешествовать вместе с вашей семьей❤️"
    },
    {
        "author":"@annabachmann5757",
        "text":"Как здорово, ребята, молодцы, что выложили этот выпуск как раз на первый Адвент 🌲❄️🌲 \nМожно сказать, что это- рождественский подарок, когда его с нетерпением ждешь и знаешь, что он обалденный ❤️\nОчень вас любим всей семьей♥️",
        "comment_id":"UgxvJoy97JmgpRYQAL54AaABAg"
    },
    {
        "comment_id":"Ugyca7c6LDlBWUbQSYh4AaABAg",
        "text":"редко пишу комментарии, но этот канал… это нечто, ребята, вы афигенные! продолжайте в том же духе! жду новые видео как день рождения ей Богу)",
        "author":"@user-nj1cv1vl1h"
    }
]
answers_format = {
   'answers': [
        {
            'comment_id': 'cid_1',
            'variants': [
                {
                    'answer_id': '0',
                    'text': 'answer 1'
                },
                {
                    'answer_id': '1',
                    'text': 'answer 2'
                }
            ]
        },    
    ]
}
for _ in range(3):
    start_time = time.time()
    prompt = f"""
I have youtube channel. Suggest {len(desired_answers)} answers for each user comment (each answer in the language of comment) under my video. Use video summary and info for context and style:
Summary: ‘The video is about anal sex’
Info: ‘You are a woman bloger, use sarcastic style’
Use answers parameters as setup for corresponding answer for each comment. ‘words_count’ - for answer length, ‘note’ - fore style and other info. Use ‘answer_id’ to refer this settings in response.
Answers parameters: ‘{desired_answers}’
Comments: ‘{comments}’
Resulting 'answers' array must contain {len(desired_answers) * len(comments)} objects. Return answer in JSON. 
JSON format:
‘{answers_format}’
"""
    # print(prompt)
    response = gpt.get_json(prompt, seed=1)
    if not response:
        print("response is empty")
        continue
    if not response.get("answers"):
        print("response.answers is empty")
        continue
    if len(response["answers"]) != len(comments):
        print(len(response["answers"]), "should be", len(comments))
        print("response.answers is not valid")
        continue
    print(len(response["answers"][0]["variants"]), len(desired_answers))
    print(response)
    elapsed_time = time.time() - start_time
    times.append(elapsed_time)
    print(f"Время выполнения запроса: {elapsed_time} секунд")

# median_time = sorted(times)[len(times)//2]
# min_time = min(times)
# max_time = max(times)
# print(f"Медианное время выполнения запроса: {median_time} секунд")
# print(f"Минимальное время выполнения запроса: {min_time} секунд")
# print(f"Максимальное время выполнения запроса: {max_time} секунд")

