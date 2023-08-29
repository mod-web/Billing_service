import json
import logging

from rmq import Rmq


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    rmq = Rmq()
    mode = 'instant'    # delayed
    users_data = [
        {
            'email': 'module-web@yandex.ru',
            'user_name': 'Andrey',
            'link': 'https://domen.com/1',
            'number_likes': 5,
            'text': 'This is promo text'
        },
        {
            'email': 'pyvaluecode@gmail.com',
            'user_name': 'Another name',
            'link': 'https://domen.com/2',
            'number_likes': 10,
            'text': 'This is promo text'
        },
    ]

    if mode == 'instant':
        body = {
            'uuid': 'eb88b8f7-2ef8-4e66-8917-1b44e5a0c9b6',
            'type_sender': 'email',
            'template_id': 4,
            'subject': 'Title',
            'data': users_data
        }
    else:
        body = {
            'uuid': 'eb88b8f7-2ef8-4e66-8917-1b44e5a0c9b6',
            'type_sender': 'email',
            'timezone': 'Europe/Moscow',
            'time_from': '23:41:00',
            'time_to': '23:59:00',
            'template_id': 3,
            'subject': 'Title',
            'data': users_data
        }

    res = rmq.publish(mode, json.dumps(body))
    logging.info(f'Sent message: {res}')
