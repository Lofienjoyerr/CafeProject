- [CafeProject](#cafe-project)
    * [Установка](#installation)
    * [Краткое описание функционала](#description)
    * [Лицензия](#license)

<!-- TOC --><a name="cafe-project"></a>
# CafeProject
Backend часть веб-приложения на Django для управления заказами в кафе.\
Код написан на Python фреймворках __[Django](https://docs.djangoproject.com/en/5.1/)__ и __[Django REST Framework](https://www.djangoproject.com/)__.
В качестве основной базы данных использует __[PostgreSQL](https://www.postgresql.org/)__, для кеширования использует __[Redis](https://github.com/redis/redis)__.
Для обработки очередей задач используется __[Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html)__, а в качестве брокера очередей – __[Redis](https://github.com/redis/redis)__.
Полнофункциональная пользовательская система основывается на JWT, реализованных с помощью библиотеки __[djangorestframework_simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)__.
Тестирование проведено с помощью фреймворка __[pytest](https://github.com/pytest-dev/pytest)__.
Имеется возможность полнотекстового поиска заказов с помощью __[Django Elasticsearch DSL](https://django-elasticsearch-dsl.readthedocs.io/en/latest/index.html)__.
Добавлена контейнеризация с помощью __[docker/compose](https://docs.docker.com/)__.
В дополнение, у проекта имеется OpenAPI схема, сгенерированная при помощи __[drf-spectacular](https://github.com/tfranzel/drf-spectacular/)__, и __Swagger UI__ для визуализации и тестирования API.
Также реализовано логирование, сохраняющееся в файл `log.log` в корневой директории.

<!-- TOC --><a name="installation"></a>
## Установка
1. Убедитесь в том, что у вас установлен docker.
2. Клонируйте репозиторий. Перейдите в созданную директорию.
```commandline
git clone https://github.com/Lofienjoyerr/CafeProject.git
cd CafeProject/
```
3. Создаём файл окружения .env и настраиваем его по примеру файла .env.template.
4. Запускаем все контейнеры.
Для первого раза:
```commandline
docker compose up -d --build
```
Для следующих:
```commandline
docker compose up -d
```
Чтобы остановить:
```commandline
docker compose down
```
5. Готово. API будет доступно по адресу `http://127.0.0.1:8000/api/v1/`, документация к нему -
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
