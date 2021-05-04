# Публикует случайный комикс с xkcd в сообщество Вконтакте
- `main.py` скачивает случайный комикс, публикует в сообщество Вконтакте, удаляет локальный файл.

## Файл переменных окружения .env

- `VK_ACCESS_TOKEN` ключ доступа к VK, получить можно [на оф. сайте Вконтакте](https://vk.com/dev/implicit_flow_user). Необходимы следующие права: `photos`, `groups`, `wall` и `offline`.
- `VK_GROUP_ID` идентификатор сообщества, посмотреть можно [здесь](https://regvk.com/id/).

## Установка

### Подготовка скрипта

1. Скачайте код и перейдите в папку проекта.
    ```bash
    git clone https://github.com/n1k0din/api-vk.git
    ```  
    ```bash
    cd api-vk
    ```
2. Установите вирт. окружение.
    ```bash
    python -m venv venv
    ```
3. Активируйте.
    ```bash
    venv\Scripts\activate.bat
    ```
    или
    ```bash
    source venv/bin/activate
    ```
4. Установите необходимые пакеты.
    ```bash
    pip install -r requirements.txt
    ```

## Запуск

```
python main.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
