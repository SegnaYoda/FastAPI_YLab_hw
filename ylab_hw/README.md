
● 
Задание со звездочкой:
● Валидировать данные при регистраций и обновлений данных пользователя


● Хранить в Redis заблокированные access_tokens (удобно хранить это в разных базах)
● Хранить в Redis активные refresh_tokens для определенного пользователя (удобно хранить
это в разных базах)
● Добавить метод выхода из аккаунта (
на этом этапе надо добавить access_token в список заблокированных токенов в Redis,
удалить refresh_token из списка активных токенов в Redis определенного пользователя
)
● Выйти со всех устройств. (удалить все активные refresh_token для определенного
пользователя)



for posts

Анонимный пользователь может:
GET api/v1/posts    GEt all   ● Просмотреть список постов.
GET api/v1/posts/{id}    Get 1      ● Просмотреть детально определенный пост.

Авторизованный пользователь может:
POST api/v1/posts         Create        ● Создать пост.
{
    "title": "Post 2",
    "description": "That's my discription ENW"
}


PATCH api/v1/posts/{id}    Update       ● Изменить пост
{"title": "Post 2", "description": "That's my discription ENW"}

DELETE api/v1/posts/{id}    Delete      ● удалить пост

____________________
for users:

Анонимный пользователь может:
POST api/v1/signup   register    ● Создать аккаунт, если выбранный username еще не зарегистрирован в системе.
{
  "username": "Krot223322",
  "password": "Qwerty123",
  "email": "Krot223322@mail.ru"
}
POST api/v1/login   login       ● Войти в свой аккаунт по username и паролю.
{
  "username": "Krot223322",
  "password": "Qwerty123"
}


Авторизованный пользователь может:
POST api/v1/refresh         ● получить новый access_token
GET api/v1/users                 ● Просмотреть список пользователей.
GET api/v1/users/me               ● Просмотреть свой профиль.
PATCH  api/v1/users/me   ● Изменить свои личные данные — email, username и др. И получить новый access_token
{
    "username": "Krot",
    "email": "w98erg@mail.ru"
}
DELETE api/v1/users/me    ● удалить пользователя




