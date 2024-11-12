import requests  # Импортируем библиотеку requests для выполнения HTTP-запросов
import time  # Импортируем библиотеку time для работы с временными задержками

# Токен бота, полученный от BotFather в Telegram
TOKEN = ''
# ID администратора, который будет управлять ботом
ADMIN_CHAT_ID = ''
# URL для доступа к API Telegram с использованием токена
URL = f'https://api.telegram.org/bot{TOKEN}/'
# Начальное значение offset для получения обновлений
OFFSET = 0

def get_updates():
    # Параметры запроса для получения обновлений от Telegram
    params = {'timeout': 100, 'offset': OFFSET}
    # Выполняем GET-запрос к API Telegram для получения обновлений
    response = requests.get(URL + 'getUpdates', params=params)
    # Преобразуем ответ в формат JSON
    result = response.json()
    # Возвращаем список обновлений
    return result['result']

def send_message(chat_id, text):
    # Параметры запроса для отправки сообщения
    params = {'chat_id': chat_id, 'text': text}
    # Выполняем POST-запрос к API Telegram для отправки сообщения
    requests.post(URL + 'sendMessage', data=params)

print("Бот запущен...")  # Сообщение о том, что бот успешно запущен

while True:  # Бесконечный цикл для постоянного получения обновлений
    try:
        updates = get_updates()  # Получаем обновления от Telegram
        for update in updates:  # Проходим по каждому обновлению
            OFFSET = update['update_id'] + 1  # Обновляем offset для получения следующих обновлений

            message = update.get('message')  # Извлекаем сообщение из обновления
            if not message:  # Если сообщение отсутствует, продолжаем к следующему обновлению
                continue

            chat_id = message['chat']['id']  # Получаем ID чата, откуда пришло сообщение
            text = message.get('text', '')  # Получаем текст сообщения, если он есть

            # Если сообщение от администратора
            if str(chat_id) == ADMIN_CHAT_ID:
                # Проверяем, есть ли ответ на пересланное сообщение
                if 'reply_to_message' in message:
                    reply = message['reply_to_message']  # Извлекаем оригинальное сообщение, на которое отвечают
                    # Извлекаем ID пользователя из текста оригинального сообщения
                    if 'forward_from' in reply:  # Проверяем, переслано ли сообщение от пользователя
                        user_id = reply['forward_from']['id']  # Получаем ID пользователя
                        send_message(user_id, text)  # Отправляем ответ пользователю
                    else:
                        send_message(ADMIN_CHAT_ID, "Не удалось определить пользователя.")  # Сообщаем администратору, что не удалось определить пользователя
                else:
                    send_message(ADMIN_CHAT_ID, "Ответьте на сообщение пользователя.")  # Сообщаем администратору, что нужно ответить на сообщение
            else:
                # Пересылаем сообщение администратору
                params = {
                    'chat_id': ADMIN_CHAT_ID,  # ID администратора
                    'from_chat_id': chat_id,  # ID чата, откуда пришло сообщение
                    'message_id': message['message_id']  # ID сообщения, которое нужно переслать
                }
                # Выполняем POST-запрос для пересылки сообщения
                requests.post(URL + 'forwardMessage', data=params)
    except Exception as e:  # Обработка исключений
        print(f"Произошла ошибка: {e}")  # Выводим сообщение об ошибке
        time.sleep(1)  # Задержка на 1 секунду перед следующей попыткой