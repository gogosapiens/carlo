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
desired_answers = [
    {
        "note":"Tone: angry",
        "text":"Insert text here",
    },
    {
        "note":"Tone: Calm",
        "text":"Insert text here",
    },
    {
        "note":"Tone: moderate",
        "text":"Insert text here",
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
        "comment_id":"Ugyca7c6LDlBWUbQSYh4AaABAg",
        "text":"редко пишу комментарии, но этот канал… это нечто, ребята, вы афигенные! продолжайте в том же духе! жду новые видео как день рождения ей Богу)",
        "author":"@user-nj1cv1vl1h"
    }
]
answers_format = {
    "answers": [
        {
            "comment_id": "comment_id",
            "answer_variants": desired_answers
        },
    ]
}
min_words_count = 3
max_words_count = 5
stats = {}
for i in range(5):
    seed = i + 5
    stats[seed] = []
    times = []
    for j in range(5):
        print(f"-----------------{seed}-{j}-------------------")
        start_time = time.time()
        prompt = f"""
    I have youtube channel. Suggest answer variants for each user comment (in the language of comment) under my video. Use video summary and info for context and style:
    Video summary: ‘The video is about anal sex’
    Info: ‘You are a woman bloger, use sarcastic style’
    Comments under video: ‘{comments}’
    Return response in JSON with format:
    ‘{answers_format}’
    Resulting 'answers' array must contain {len(comments)} objects with {len(desired_answers)} answers variants in each. 
    Each variant must contain ‘text’ - your suggested answer text which is more than {min_words_count} but less than {max_words_count} words length. 
    The words count of 'text' in each variant is very important (more than {min_words_count} but less than {max_words_count} words).
    Consider ‘note’ as style and other info for each variant, don't include 'note' key in resulting json.
    """
        print(prompt)
        response = gpt.get_json(prompt, seed=seed)
        if not response:
            print("response is empty")
            stats[seed].append(False)
            continue
        if not response.get("answers"):
            print("response.answers is empty")
            stats[seed].append(False)
            continue
        if len(response["answers"]) != len(comments):
            print(len(response["answers"]), "should be", len(comments))
            print("response.answers is not valid")
            stats[seed].append(False)
            continue
        print(response)
        if len(response["answers"]) != len(comments):
            print("response.answers is not valid")
            stats[seed].append(False)
            continue
        if len(response["answers"][0]["answer_variants"]) != len(desired_answers):
            print("response.answers[0].answer_variants is not valid")
            stats[seed].append(False)
            continue
        for answer in response["answers"]:
            break_loop = False
            for answer_variant in answer["answer_variants"]:
                if not answer_variant.get("text"):
                    print("answer_variant.text is empty")
                    stats[seed].append(False)
                    break_loop = True
                    break
                words_count = len(answer_variant["text"].split())
                if words_count < (min_words_count / 1.5) or words_count > (max_words_count * 1.5):
                    print("answer_variant.text is not valid,", words_count, "words")
                    stats[seed].append(False)
                    break_loop = True
                    break
            if break_loop:
                break
        elapsed_time = time.time() - start_time
        times.append(elapsed_time)
        print(f"Время выполнения запроса: {elapsed_time} секунд")

        legacy_answers = []
        for answer in response["answers"]:
            for index, answer_variant in enumerate(answer["answer_variants"]):
                legacy_answers.append({
                    "comment_id": answer["comment_id"],
                    "answer_id": str(index),
                    "text": answer_variant["text"],
                })

        legacy_response = {
            "answers": legacy_answers
        }
        print("***")
        print(legacy_response)
        exit(0)

    print("***")
    median_time = sorted(times)[len(times)//2]
    min_time = min(times)
    max_time = max(times)
    print(f"Медианное время выполнения запроса: {median_time} секунд")
    print(f"Минимальное время выполнения запроса: {min_time} секунд")
    print(f"Максимальное время выполнения запроса: {max_time} секунд")

for seed, errors in stats.items():
    print(f"seed: {seed}, errors count: {len(errors)}")

# seed: 0, errors count: 8
# seed: 1, errors count: 8
# seed: 2, errors count: 8
# seed: 3, errors count: 7
# seed: 4, errors count: 1

# seed: 0, errors count: 5
# seed: 1, errors count: 0
# seed: 2, errors count: 0
# seed: 3, errors count: 0
# seed: 4, errors count: 0

# seed: 0, errors count: 2
# seed: 1, errors count: 1
# seed: 2, errors count: 0
# seed: 3, errors count: 0
# seed: 4, errors count: 0

# seed: 5, errors count: 0
# seed: 6, errors count: 0
# seed: 7, errors count: 0
# seed: 8, errors count: 3
# seed: 9, errors count: 0

# seed: 5, errors count: 2
# seed: 6, errors count: 0
# seed: 7, errors count: 0
# seed: 8, errors count: 1
# seed: 9, errors count: 0