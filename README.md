Команды для первоначального запуска контейнеров:
`docker-compose up -d --build`
Для применения миграций в Postgres:
`alembic upgrade head`

В коллекции postman существует ряд неточностей:

- В пункте "Заходит на сайт" и "Повторно заходит на сайт"  указан конкретный пользователь "pr_zoom@mail.ru" для входа, не тестовый (т.е. он еще не зарегистрирован). Изменил на {{test user}}
- В пункте "Обновляет информацию о себе" в графе username не стоят двоянные ковычки, что генерирует ошибку, исправил.
- В пункте "Выйти из аккаунта" и "Выйти из всех устройств" не указан не localhost, исправил на {{LOCAL_URL}}.
- В пункте "Выйти из аккаунта" и "Выйти из всех устройств" в запросе не указан access token, исправил.

Исправленную коллекцию для теста прилагаю в корневом каталоге.


Реализовано:

По разделу "Пост":

Анонимный пользователь может:

- Просмотреть список постов. 
`GET api/v1/posts`
- Просмотреть детально определенный пост.
`GET api/v1/posts/{id}`

Авторизованный пользователь может:

- Создать пост. `POST api/v1/posts`
`{"title": "Post 2", "description": "That's my discription ENW"}`

- Изменить пост. `PATCH api/v1/posts/{id}`
`{"title": "Post 2", "description": "That's my discription ENW"}`

- Удалить пост. `DELETE api/v1/posts/{id}`
____________________
По разделу "Пользователь":

Анонимный пользователь может:
- Создать аккаунт, если выбранный username еще не зарегистрирован в системе. `POST api/v1/signup` 
`{"username": "test_username","password": "test_password","email": "email@mail.ru"}`
- Войти в свой аккаунт по username и паролю. `POST api/v1/login`
`{"username": "test_username", "password": "test_password"}`

Авторизованный пользователь может:
- получить новый access_token. `POST api/v1/refresh` 
- Просмотреть список пользователей. `GET api/v1/users`
- Просмотреть свой профиль. `GET api/v1/users/me`
- Изменить свои личные данные — email, username и др. И получить новый access_token. `PATCH  api/v1/users/me`
`{"username": "new_test_username", "email": "new_email@mail.ru"}`
- удалить пользователя. `DELETE api/v1/users/me` 

Выполнено задание со звездочкой:
- Данные валидируются через schema при регистрациb и обновлениях данных пользователя.
- В Redis хранятся заблокированные access_tokens. db1
- В Redis хранятся активные refresh_tokens для определенного пользователя. db2
- Добавлен метод выхода из аккаунта (на этом этапе access_token переносится из db0 d db1 - в список заблокированных токенов в Redis, удаляется refresh_token из списка активных токенов в Redis определенного пользователя).
- Добавлен метод Выйти со всех устройств. (удаляюся все активные refresh_token для определенного
пользователя db2). 

Также в Redis хранятся новые посты и пользователи для более быстрого доступа к данным.