# Телеграм бот justice_python_bot
### Бот создан для удобной проверки судебных дел на [официальном портале судов общей юрисдикции города Москвы ][Мосгорсуд]

#### Version 2: Добавлен модуль автоматической проверки новых дел! В случае появления нового дела бот присылает уведомление в телеграм!
#### 

![Dave_Kosak](https://static.wikia.nocookie.net/hearthstone_gamepedia/images/6/69/Dave_Kosak_full.jpg)

##### В боте реализован следующий функционал:
 - Сохранение chat_id нового пользователя в БД для последующей идентификации
 - Возможность добавления ФИО и/или номера дела
 - Проверка судебных дел по ФИО и/или номеру дела
 - Отправка результатов поиска в телеграм пользователя 
 
Для взаимодействия с ботом необходимо найти его в телеграме [justice_python_bot][Бот] и нажать кнопку ✨/**start**✨
    
### Технологии
| Имя | Ссылка |
| ------ | ------ |
| модуль бота | [python-telegram-bot 13.7][python-telegram-bot] |
| модуль парсера | [beautifulsoup4 4.12.2][beautifulsoup4] |
| python dotenv | [python-dotenv 1.0.0][dotenv] |
| requests | [requests 2.31.0][requests] |
| Docker Compouse | [overview][docker] |
| Nginx | [documentation][nginx] |
| PostgreSQL | [13.12 Documentation][PostgreSQL] |

### Автор 

**Эльдар Барбаросса** 

[//]: # (links)

   [Мосгорсуд]: <https://mos-gorsud.ru>
   [Бот]: <https://t.me/Justice_barba_bot>
   [python-telegram-bot]: <https://docs.python-telegram-bot.org/en/v13.7/>
   [beautifulsoup4]: <https://pypi.org/project/beautifulsoup4/>
   [dotenv]: <https://pypi.org/project/python-dotenv/>
   [requests]: <https://pypi.org/project/requests/>
   [docker]: <https://docs.docker.com/compose/>
   [nginx]: <https://nginx.org/en/docs/>
   [PostgreSQL]: <https://www.postgresql.org/docs/13/index.html>

