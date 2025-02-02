- [CafeProject](#cafe-project)
    * [Установка](#installation)
    * [Краткое описание функционала](#description)
    * [Лицензия](#license)

<!-- TOC --><a name="cafe-project"></a>
# CafeProject
Backend часть веб-приложения на Django для управления заказами в кафе.\
Код написан на Python фреймворках __[Django](https://docs.djangoproject.com/en/5.1/)__ и __[Django REST Framework](https://www.djangoproject.com/)__.
В качестве основной базы данных использует __[PostgreSQL](https://www.postgresql.org/)__, для кеширования использует __[Redis](https://github.com/redis/redis)__.
Для обработки очередей задач используется __[Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html)__, а в качестве брокера сообщений – __[Redis](https://github.com/redis/redis)__.
Полнофункциональная пользовательская система основывается на JWT, реализованных с помощью библиотеки __[djangorestframework_simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)__.
Тестирование проведено с помощью фреймворка __[pytest](https://github.com/pytest-dev/pytest)__.
В дополнение, у проекта имеется OpenAPI схема, сгенерированная при помощи __[drf-spectacular](https://github.com/tfranzel/drf-spectacular/)__, и __Swagger UI__ для визуализации и тестирования API.

<!-- TOC --><a name="installation"></a>
## Установка
Перед установкой убедитесь, что у вас установлен __Python__, менеджер пакетов __pip__ и
средство создания виртуальных окружений __venv__.
Данная инструкция будет использовать именно эти инструменты. Также инструкция направлена на пользователей Windows.
Для пользователей Unix-систем алгоритм в общем будет такой же, но небольшие отличия приводить не будем.
1. Клонируем репозиторий
```commandline
git clone https://github.com/Lofienjoyerr/CafeProject.git
cd CafeProject/
```
2. Создаём виртуальное окружение и активируем его
```commandline
python -m venv .venv
.venv/Scripts/activate
```
3. Скачиваем и устанавливаем все зависимости
```commandline
pip install -r requirements.txt
```
5. (Optional) Если вы хотите запустить сервер в режиме debug, то также установите
```commandline
pip install django-debug-toolbar
pip install ipython
pip install django-extensions
```
6. Создаём базу данных (СУБД можете выбирать на ваше предусмотрение. Инструкции для установки выбранной СУБД и создания БД
найдите самостоятельно)
7. Создаём файл окружения `.env` и настраиваем его по примеру файла `.env.template`
8. Применяем миграции
```commandline
python manage.py migrate
```
9. Запускаем сервер
```commandline
python manage.py runserver
```
10. Готово. API будет доступно по адресу `http://127.0.0.1:8000/api/v1/`, документация к нему -
`http://127.0.0.1:8000/api/v1/schema/`, а Swagger UI - `http://127.0.0.1:8000/api/v1/swagger/`.

<!-- TOC --><a name="description"></a>
## Краткое описание функционала
1. Пользовательская система
   - Получение списка всех пользователей (с пагинацией).
   - Получение информации о конкретном пользователе. Возможность изменения его информации.
   - Возможность авторизации через JWT. Получение информации о пользователе через токен.
   - Возможность изменять и восстанавливать пароль через электронную почту.
   - Регистрация пользователя с подтверждением электронной почты.
   - Изменение адреса электронной почты с последующим подтверждением нового.
2. Управление кафе
   - Вычисление суммарного дохода с оплаченных заказов за определённый день.
   - Добавление заказа с автоматически рассчитанной стоимостью и статусом "в ожидании".
   - Удаление заказа по выбранному ID.
   - Отображение всех заказов (с пагинацией).
   - Возможность фильтрации списка заказов по нескольким параметрам.
   - Изменение информации заказа по его ID.

<!-- TOC --><a name="license"></a>
## Лицензия
У этого проекта [MIT лицензия](https://github.com/Lofienjoyerr/CafeProject/blob/main/LICENSE).
