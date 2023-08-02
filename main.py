
import json
from dataclasses import dataclass

import requests

from tqdm.auto import tqdm as log_progress


def read_lines(path):
    with open(path) as file:
        for line in file:
            yield line.rstrip('\n')


def write_lines(path, lines):
    with open(path, 'w') as file:
        for line in lines:
            file.write(line + '\n')


def parse_jsonl(lines):
    for line in lines:
        yield json.loads(line)


def format_jsonl(items):
    for item in items:
        yield json.dumps(item, ensure_ascii=False)


def item_prompt(item):
    prompt = item['instruction']
    input = item.get('input')
    if input:
        prompt += '\nДано: ' + input
    return prompt


def parse_headers(value):
    for line in value.splitlines():
        index = line.find(': ')
        if index > 0:
            yield line[:index], line[index + 2:]


########
#
#   GIGACHAT
#
#######


HEADERS = dict(parse_headers('''
Content-Type: application/json
Cookie: _sm_sess=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJqdGkiOiI1MDY1MjY5Ni1mYWViLTQ3YWUtOWUzNC00NWZhM2Y1ODRkZDMiLCJzdWIiOiIwNjcxZjNkZjllYjlkMjIzOTlmMTU5NDNhNTAxNDQxMmI3MzVlOTg1NWNjNzEyZDNhNzUwZTA3ZTYxMGI0NTQ5NTM5YmU5MjcwMDQyNjI5OCIsImlzcyI6IktFWU1BU1RFUiIsImV4cCI6MTY5MDk1Mzc3NCwiYXVkIjoiREVWRUxPUEVSX1BPUlRBTCIsInVzciI6ImVhYjNhYTAzLTBlMjktNGYyOS1iYmMxLTcxNDc3YzNkNGUyYSIsImlhdCI6MTY5MDk1MTk2NCwidHlwZSI6IkJlYXJlciIsInNpZCI6ImM3NDE4N2UyLTIwMmUtNDEzZi1hNjM4LTQ5YzFlNTJkYTc5MiJ9.SMuIdyt1ZDwlM4zjzLC8lWv4cVoYfdgxscjRqyAV2svdE6sGHWgZElbkUFyKOT9QCs5Cv3B5SG1ofaPLYkG0WNzrZnm_VRplUtQKY__YM9r4IUO4MO6nF0XMKQilbHtrvtMG2BcKAmAQpSBsz6Py7x6LHyZ51770kHfVOzuglCjoZht4c355wiAQiLzdq4u1w5J0A81HuiNn-9jkT0M-dKZQL9_at-0gkUuhKMyO_lAqutz1dp7lm5ybZ07VFwk8myTj7HlPhq1Gqk88giTW0UsrV-69cTkxsIIV-EVc-aWF7hB85ompndhL75ywV296KDhzyICc-l8WDvBVtDFsFH30DQdOdp1uZtA3yC9o3RwS6gMeMpjuT0T8xR0sFhOsDaGGzxg3O5iwUJtw2ND-BsHCQm4i4XSlA_R_3iQaUGD9rz-xHhAQiEYfj501gdwgBMmha91HFFUVhZVc_UJf3g0fWbW9R3cuC0VlVmcS0qRRrBotUWYSQbTCq36huyQggbDNrKp1LAIBkxWCWd0xbLztBL6fSUuWwMAZasvq3JRfJGWHnSWC-0EoTOIc88XfVGg_oPssxGpwEodnHT782GM_3B18pChGUi_NweY2LCuol6WzZ1kUZ6EStxB6E7x-MeQPk4tyxtg6YuTZGp_4a8ihsmy-eewiZ02ZH6ad-iU; _sm_user_id=eab3aa03-0e29-4f29-bbc1-71477c3d4e2a; sticky_cookie_dp=2668b030f58b3efd; sticky_cookie_km=f5e5454e6e94ffe5; CRON=acff5ee7c28c708c6ffe998ee063f47a; sticky_cookie_cgw=d1d5685d6e85368d
Host: developers.sber.ru
Origin: https://developers.sber.ru
Pragma: no-cache
Referer: https://developers.sber.ru/studio/workspaces/545c90ee-6848-4475-a469-5c5e1f48a282/ml/projects/45d2984b-53ff-451c-aa73-4b0cf6d01891/sessions/61a3bdb6-70e3-4fe6-8c01-13253ee3845d
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
space-id: 545c90ee-6848-4475-a469-5c5e1f48a282
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15
user-id: 45d2984b-53ff-451c-aa73-4b0cf6d01891
X-Request-Id: a9251d0c-1d37-4b53-a9ba-dc912b27a975
'''))


SESSION_ID = '61a3bdb6-70e3-4fe6-8c01-13253ee3845d'
SPACE_ID = HEADERS['space-id']
USER_ID = HEADERS['user-id']


def gigachat_session_messages(session_id, offset=0, limit=10):
    response = requests.post(
        'https://developers.sber.ru/api/chatwm/api/client/session_messages',
        headers=HEADERS,
        json={
            'offset': offset,
            'limit': limit,
            'session_id': session_id,
            'newer_first': True
        }
    )
    response.raise_for_status()
    return response.json()


# {'total_messages': 6,
#  'messages': [{'side': 'model',
#    'request_id': 'aaf5d915-80ce-4594-9c66-6483c3ff0561',
#    'date': '2023-08-01T18:41:30.433714Z',
#    'model_type': 'GigaChat:v1.13.0',
#    'model_type_display_name': 'GigaChat:v1.13.0',
#    'preset': 'default',
#    'preset_display_name': 'По умолчанию',
#    'response_id': 4555526,
#    'set_by_user': False,
#    'data': 'Python и JavaScript — это два разных языка программирования, которые имеют ряд различий. Вот некоторые из основных различий:\n\n1. Синтаксис: Синтаксис Python более прямолинеен и прост, в то время как синтаксис JavaScript более гибкий и позволяет использовать различные конструкции для достижения одной и той же цели.\n\n2. Библиотеки: Python имеет большое количество библиотек, которые упрощают многие задачи, в то время как JavaScript имеет меньше библиотек, но они более специализированные и ориентированы на веб-разработку.\n\n3. Объектно-ориентированное программирование: Python является объектно-ориентированным языком, что означает, что объекты являются основной единицей языка и могут использоваться для представления данных и функциональности программы. JavaScript также является объектно-ориентированным языком, но он больше ориентирован на веб-разработку и использует прототипирование для создания интерактивных пользовательских интерфейсов.\n\n4. Читаемость кода: Python обычно считается более читаемым языком, поскольку он использует отступы для разделения кода и делает код более понятным. JavaScript, с другой стороны, часто используется без отступов, что делает его более легким для чтения, но может привести к менее понятному коду.\n\n5. Безопасность: Python известен своей безопасностью, благодаря использованию сильных типов данных и проверок безопасности. JavaScript, с другой стороны, менее безопасен, поскольку он не использует проверки типов и может быть уязвим к SQL-инъекциям и другим видам атак.\n\n6. Масштабируемость: Python хорошо подходит для разработки масштабируемых приложений, так как он поддерживает динамическую типизацию и может обрабатывать большие объемы данных. JavaScript, с другой стороны, лучше подходит для разработки простых веб-приложений, которые могут работать на небольших объемах данных.'},
#   {'side': 'user',
#    'request_id': 'aaf5d915-80ce-4594-9c66-6483c3ff0561',
#    'date': '2023-08-01T18:41:28.917282Z',
#    'model_type': 'GigaChat:v1.13.0',
#    'model_type_display_name': 'GigaChat:v1.13.0',
#    'preset': 'default',
#    'preset_display_name': 'По умолчанию',
#    'model_status': 'ready',
#    'request_json': 'В чем основные различия между языками программирования Python и JavaScript?'},
#   {'side': 'model',
#    'request_id': '31646125-e6d0-40e8-89a8-3c4e829628ae',
#    ...


@dataclass
class GigachatMessage:
    side: str
    text: str


def parse_session_messages(data):
    for item in data['messages']:
        side = item['side']
        assert side in ('user', 'model'), side
        if side == 'user':
            text = item['request_json']
        elif side == 'model':
            text = item['data']
        yield GigachatMessage(side, text)

            
def message_prompt_answers(messages):
    for index, message in enumerate(messages):
        if index == 0:
            assert message.side == 'model'

        if message.side == 'model':
            prev_message = messages[index + 1]
            assert prev_message.side == 'user'
            yield prev_message.text, message.text


def gigachat_request(prompt, session_id):
    response = requests.post(
        'https://developers.sber.ru/api/chatwm/api/client/request',
        headers=HEADERS,
        json={
            'generate_alternatives': False,
            'request_json': prompt,
            'session_id': session_id,
            'model_type': 'GigaChat:v1.13.0',
            'preset': 'default'
        }
    )
    response.raise_for_status()
    return response.json()


# {
#     "result": "accepted",
#     "request_id": "5a9c58ff-bd31-4e97-bb6c-065534f614f4",
#     "generation_start_estimation_seconds": 0.1415866
# }
    

def parse_gigachat_request(data):
    assert data.get('result') == 'accepted', data
    return data['request_id']


def gigachat_result_events(request_id, space_id, user_id):
    response = requests.get(
        'https://developers.sber.ru/api/chatwm/api/client/get_result_events',
        params={
            'request_id': request_id,
            'space-id': space_id,
            'user-id': user_id,
        },
        headers=HEADERS,
        stream=True
    )
    response.raise_for_status()
    return response.iter_lines()


# {'status': 'in_progress', 'next_update_estimation_seconds': 8.0, 'model_type': 'GigaChat:v1.13.0', 'model_type_display_name': 'GigaChat:v1.13.0', 'responses': [{'id': 4580829, 'data': 'Если бы ... открыли Америку, возможно, что'}]}


@dataclass
class GigachatResultEvent:
    status: str
    text: str


def parse_gigachat_result_events(lines):
    for line in lines:
        line = line.decode('utf8')
        if not line.startswith('data: '):
            continue
            
        line = line[len('data: '):]
        item = json.loads(line)
        yield GigachatResultEvent(
            status=item['status'],
            text=item['responses'][0]['data']
        )


def ready_event_text(events):
    for event in events:
        if event.status == 'ready':
            return event.text
