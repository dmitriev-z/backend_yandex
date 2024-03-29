# Yandex Backend School Task
[![version][version-badge]][CHANGELOG]

REST API сервис для обработки выгрузок данных интернет-магазина подарков.

## Содержание
>1\. [Описание сервиса](https://github.com/dmitriev-z/backend_yandex#1-описание-сервиса)
>>1.1 [Обработчики запросов](https://github.com/dmitriev-z/backend_yandex#11-обработчики-запросов)    
>>>1.1.1 [POST /imports](https://github.com/dmitriev-z/backend_yandex#111-post-imports)  
>>>1.1.2 [PATCH /imports/$import_id/citizens/$citizen_id](https://github.com/dmitriev-z/backend_yandex#112-patch-importsimport_idcitizenscitizen_id)   
>>>1.1.3 [GET /imports/$import_id/citizens](https://github.com/dmitriev-z/backend_yandex#113-get-importsimport_idcitizens)  
>>>1.1.4 [GET /imports/$import_id/citizens/birthdays](https://github.com/dmitriev-z/backend_yandex#114-get-importsimport_idcitizensbirthdays)  
>>>1.1.5 [GET /imports/$import_id/towns/stat/percentile/age](https://github.com/dmitriev-z/backend_yandex#115-get-importsimport_idtownsstatpercentileage)
>>
>>1.2 [Управление сервисом](https://github.com/dmitriev-z/backend_yandex#12-управление-сервисом)
>
>2\. [Установка сервиса](https://github.com/dmitriev-z/backend_yandex#2-установка-сервиса)
>>2.1 [Установка требуемых пакетов](https://github.com/dmitriev-z/backend_yandex#21-установка-требуемых-пакетов)  
>>2.2 [Установка MongoDB Community Edition](https://github.com/dmitriev-z/backend_yandex#22-установка-mongodb-community-edition)  
>>2.3 [Создание виртуального окружения](https://github.com/dmitriev-z/backend_yandex#23-создание-виртуального-окружения)  
>>2.4 [Установка требуемых python библиотек](https://github.com/dmitriev-z/backend_yandex#24-установка-требуемых-python-библиотек)
>
>3\. [Запуск сервиса](https://github.com/dmitriev-z/backend_yandex#3-запуск-сервиса)
>>3.1. [Запуск сервиса локально](https://github.com/dmitriev-z/backend_yandex#31-запуск-сервиса-локально)  
>>3.2. [Запуск на удаленном сервере](https://github.com/dmitriev-z/backend_yandex#32-запуск-на-удаленном-сервере)
>
>4\. [Тестирование сервиса](https://github.com/dmitriev-z/backend_yandex#4-тестирование-сервиса)

## 1. Описание сервиса
Сервис написан на `Python 3.6` и запущен в виртуальной окружении с именем `env`.    
Сервис развернут на виртуальной машине `84.201.156.229` на порту `8080` .  
В качестве хранилища данных используется NoSQL база данных MongoDB Community Edition. 
База данных развернута на той же виртуальной машине на порту `27017`.

### 1.1. Обработчики запросов
Сервис поддерживает 3 обработчика запросов:

|**№**|**URL**| **Method**| 
|:---:|---|:---:| 
|1|`http://84.201.156.229/imports`|*POST*|
|2|`http://84.201.156.229/imports/$import_id/citizens/$citizen_id`|*PATCH*|
|3|`http://84.201.156.229/imports/$import_id/citizens`|*GET*|
|4|`http://84.201.156.229/imports/$import_id/citizens/birthdays` |*GET*|
|5|`http://84.201.156.229/imports/$import_id/towns/stat/percentile/age`|*GET*|

#### 1.1.1 POST /imports
Принимает на вход набор с данными о жителях в формате json и сохраняет его с уникальным идентификатором import_id.  
В наборе данных для каждого жителя должны присутствовать все поля, значения не могут быть null , порядок полей не важен:

|**Поле** | **Тип** | **Значение** |
|:---:|:---:|---|
|citizen_id| целое число| Уникальный идентификатор жителя, неотрицательное число.|
|town| строка| Название города. Непустая строка, содержащая хотя бы 1 букву или цифру, не более 256 символов.|
|street| строка| Название улицы. Непустая строка, содержащая хотя бы 1 букву или цифру, не более 256 символов.|
|building| строка| Номер дома, корпус и строение. Непустая строка,содержащая хотя бы 1 букву или цифру, не более 256 символов.|
|apartment| целое число| Номер квартиры, неотрицательное число.|
|name| строка| Непустая строка, не более 256 символов.|
|birth_date| строка| Дата рождения в формате ДД.ММ.ГГГГ (UTC +0). Должна быть меньше текущей даты.|
|gender| строка| Значения male , female.|
|relatives| список из целых чисел| Ближайшие родственники, уникальные значения существующих citizen_id жителей из этой же выгрузки.|

Пример запроса:
```
POST /imports
{
    "citizens": [
        {
            "citizen_id": 1,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Иван Иванович",
            "birth_date": "26.12.1986",
            "gender": "male",
            "relatives": [2]
        },
        {
            "citizen_id": 2,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Сергей Иванович",
            "birth_date": "01.04.1997",
            "gender": "male",
            "relatives": [1]
        },
        {
            "citizen_id": 3,
            "town": "Керчь",
            "street": "Иосифа Бродского",
            "building": "2",
            "apartment": 11,
            "name": "Романова Мария Леонидовна",
            "birth_date": "23.11.1986",
            "gender": "female",
            "relatives": []
        }
    ]
}
```
В случае успешного добавления данных сервис вернет ответ с HTTP статусом `201 Created` и идентификатором импорта:
```
HTTP 201
{
    "data": {
        "import_id": 1
    }
}
```
В случае, если входные данные не прошли валидацию 
(данные не были переданы, отсутствуют обязательные поля, присутсвуют неописанные поля, неправильное значение поля), 
сервис вернет ответ `400: Bad Request`.

#### 1.1.2. PATCH /imports/$import_id/citizens/$citizen_id
Изменяет информацию о жителе `$citizen_id` в указанном наборе данных `$import_id`.
На вход подается JSON в котором можно указать любые данные о жителе, кроме `citizen_id` : `name` , `gender` , `birth_date (UTC)`, `relatives` , `town` , `street` , `building` , `apartment` .  
В запросе должно быть указано хотя бы одно поле, значения не могут быть null.

Пример запроса:
```
PATCH /imports/1/citizens/3
{
    "name": "Иванова Мария Леонидовна",
    "town": "Москва",
    "street": "Льва Толстого",
    "building": "16к7стр5",
    "apartment": 7,
    "relatives": [1]
}
```
В случае успешного обновления данных сервис вернет ответ с HTTP статусом `200 OK` и актуальную информацию об указанном жителе:
```
HTTP 200
{
    "data": {
        "citizen_id": 3,
        "town": "Москва",
        "street": "Льва Толстого",
        "building": "16к7стр5",
        "apartment": 7,
        "name": "Иванова Мария Леонидовна",
        "birth_date": "23.11.1986",
        "gender": "female",
        "relatives": [1]
    }
}
```
В случае, если входные данные не прошли валидацию (данные не были переданы, присутсвуют неописанные поля, неправильное значение поля), сервис вернет ответ `400: Bad Request`.

#### 1.1.3. GET /imports/$import_id/citizens
Возвращает список всех жителей для указанного набора данных. 
 
Если набор данных `$import_id` присутствует в базе данных, то сервис вернет список всех citizens этого набора данных:
```
HTTP 200
{
    "data": [
        {
            "citizen_id": 1,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Иван Иванович",
            "birth_date": "26.12.1986",
            "gender": "male",
            "relatives": [2,3]
        },
        {
            "citizen_id": 2,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Сергей Иванович",
            "birth_date": "01.04.1997",
            "gender": "male",
            "relatives": [1]
        },
        {
            "citizen_id": 3,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванова Мария Леонидовна",
            "birth_date": "23.11.1986",
            "gender": "female",
            "relatives": [1]
        }
    ]
}
```
Если набор данных `$import_id` отсутсвует в базе данных, то сервис вернет ответ `400: Bad Request`.

#### 1.1.4. GET /imports/$import_id/citizens/birthdays
Возвращает жителей и количество подарков, которые они будут покупать своим ближайшим родственникам (1-го порядка), 
сгруппированных по месяцам из указанного набора данных.  
Если в импорте в каком-либо месяце нет ни одного жителя с днями рождения
ближайших родственников, значением такого ключа должен быть пустой список.  

Если набор данных `$import_id` присутствует в базе данных, сервис вернет список жителей и количество подарков, 
которые они будут покупать своим ближайшим родственникам, сгруппированных по месяцам из указанного набора данных:
```
HTTP 200
{
    "data": {
        "1": [],
        "2": [],
        "3": [],
        "4": [{
            "citizen_id": 1,
            "presents": 1,
        }],
        "5": [],
        "6": [],
        "7": [],
        "8": [],
        "9": [],
        "10": [],
        "11": [{
            "citizen_id": 1,
            "presents": 1
        }],
        "12": [
            {
                "citizen_id": 2,
                "presents": 1
            },
            {
                "citizen_id": 3,
                "presents": 1
            }
        ]
    }
}
```
Если набор данных `$import_id` отсутсвует в базе данных, то сервис вернет ответ `400: Bad Request`.

#### 1.1.5. GET /imports/$import_id/towns/stat/percentile/age
Возвращает статистику по городам для указанного набора данных `$import_id` в разрезе возраста (полных лет) жителей: 
`p50`, `p75`, `p99`, где число - это значение перцентиля.  
Если набор данных `$import_id` присутствует в базе данных, 
сервис вернет статистику по городам в разрезе возраста (полных лет) жителей:
```
HTTP 200
{
    "data": [
        {
            "town": "Москва",
            "p50": 35.0,
            "p75": 47.5,
            "p99": 59.5
        },
        {
            "town": "Санкт-Петербург",
            "p50": 45.0,
            "p75": 52.5,
            "p99": 97.15
        }
    ]
}
```
Если набор данных `$import_id` отсутсвует в базе данных, то сервис вернет ответ `400: Bad Request`.

### 1.2. Управление сервисом
Для управления сервисом на виртуальной машине был создан системный сервис `yandexbackend`.  
Конфигурационный файл сервиса доступен по пути `/etc/systemd/system/yandexbackend.service`.

Для остановки сервиса выполните в терминале следующую команду:
```shell script
sudo systemctl stop yandexbackend
```
Для запуска сервиса выполните в терминале следующую команду:
```shell script
sudo systemctl stop yandexbackend
```
Для перезагрузки сервиса выполните в терминале следующую команду:
```shell script
sudo systemctl restart yandexbackend
```
Для просмотра состояния сервиса выполните в терминале следующую команду:
```shell script
sudo systemctl status yandexbackend
```

## 2. Установка сервиса
Для установки сервиса в первую очередь необходимо склонировать данный репозиторий.  
После этого перейдите в папку с склонироованным репозиторием.

### 2.1. Установка требуемых пакетов
Для работы с python библиотеками необходимо установить менеджер пакетов [pip](https://pip.pypa.io/en/stable/).  
Для установки `pip` выполните в терминале следующие команды:
```shell script
sudo apt-get update
sudo apt-get install python3-pip
```

### 2.2 Установка MongoDB Community Edition
Подробная инструкция по установке MongoDB Community Edition представлена на [официальном сайте](https://docs.mongodb.com/v3.2/administration/install-community/).  
После установки базы данных необхродимо включить её автозапуск после перезагрузки машины.
Для этого выполните в терминале следующую команду:
```shell script
sudo systemctl enable mongod
```

### 2.3. Создание виртуального окружения
Для корректной работы сервиса необходимо изолировать его от других python-приложений. Для этого необходимо создать виртуальное окружение.  
Для работы с виртуальными окружениями необходимо установить библиотеку [virtualenv](https://virtualenv.pypa.io/en/latest/)
Для установки `virtualenv` выполните в терминале следующую команду:
```shell script
sudo pip3 install virtualenv
```
Далее необходимо создать виртуальную окружение. Для этого выполните в терминале следующую команду:
```shell script
virtualenv {env_name}
```
Данная команда создаст новое виртуальное окружение с именем `{env_name}` в катологе `{env_name}` текущей директории.

Далее необходимо включить созданное виртуальное окружение. Для этого выполните в терминале следующую команду:
```shell script
source {env_name}/bin/activate
```

### 2.4. Установка требуемых python библиотек
Для работы сервиса необходима установка следующих python-библиотек:
- [Flask](https://palletsprojects.com/p/flask/)  
Flask - фреймворк WSGI веб-приложений.
- [Gunicorn](https://gunicorn.org/)  
Gunicorn - WSGI HTTP сервер.
- [Cerberus](http://docs.python-cerberus.org/en/stable/)  
Cerberus - библиотека, предоставляющая инструменты для валидации данных.
- [Pymongo](https://api.mongodb.com/python/current/index.html)  
Pymongo - библитотека, предоставляющая инструменты для работы с MongoDB.
- [Pytest](https://docs.pytest.org/en/latest/)  
Pytest - библиоткека для написания тестов. 
- [Requests](https://2.python-requests.org/en/master/)  
Requests - библиотека для работы с HTTP забросами. В данном проекте используется в тестах.
- [Numpy](https://numpy.org/)  
Numpy - библиотека для научных вычислений.

Все требуемые библиотеки описаны в файле `requirements.txt`.  
Для установки требуемых библиотек выполните в терминале следующую команду:
```shell script
sudo pip3 install -r requirements.txt
```

## 3. Запуск сервиса

### 3.1. Запуск сервиса локально
Для запуска сервиса локально необходимо указать фрейворку Flask с каким приложением работать.  
Для этого, находясь в корневом каталоге сервиса, выполните в терминале следующую команду:
```shell script
export FLASK_APP=service.service_api.py
```
После этого можно запустить сервис, выполнив в терминале следующую команду:
```shell script
flask run
```
Данная команда запустит сервис на локальной машине на порту `5000`.

Если вы хотите запустить сервис на другом порту, то задайте аргумент `--port` при выполнениее предыдущей команды:
```shell script
flask run --port={port_to_run_app}
```
Таким образом приложение будет запущено на порту `{port_to_run_app}`

### 3.2. Запуск на удаленном сервере

Для удобства работы с сервисом на удаленном сервере необходимо создать соответсвующий системный сервис.  
Конечно, можно было бы запустить сервис вручную, но системный сервис  позволит автоматически запускать Gunicorn и обслуживать приложение Flask через систему инициализации.

Для создания системного сервиса необходимо создать файл с расширением `.service` в каталоге `/etc/systemd/system`.  
Для этого выполните в терминале следующую команду:
```shell script
sudo touch /etc/systemd/system/{service_name}.service
```
Где `{service_name}` - имя создаваемого системного сервиса.

Далее с помощью текстового редактора (nano, vim) необходимо добавить в созданный файл следующую информацию:
```text
[Unit]
Description=Gunicorn instance to serve service
After=network.target
[Service]
User={user}
Group=www-data
WorkingDirectory={service_directory}
Environment="PATH={service_directory}/env/bin"
ExecStart={service_directory}/env/bin/gunicorn --workers 1 --bind 0.0.0.0:{service_port} service.wsgi:app
[Install]
WantedBy=multi-user.target
```
Раздел `[Unit]` определяет метаданные и зависимости приложения. 
 
В разделе `[Service\` указываются:
1. Пользователь `User={user}` и группа `Group=www-data`, с помощью которых будет запущен сервис.  
2. Рабочий каталог сервиса `WorkingDirectory={service_directory}`, а так же путь к виртуальному окружению `Environment="PATH={service_directory}/env/bin"`.
3. Команда, с помощью которйо будет запускаться сервис `ExecStart={service_directory}/env/bin/gunicorn --workers 1 --bind 0.0.0.0:{service_port} service.wsgi:app`  
Согласно данной команде, система будет запускать один рабочий процесс на порту `{service_port}`.

Раздел `[Install]` определяет, к чему должен подключиться сервис во время автозапуска.

Закройте файл, сохранив изменения.

Далее необходимо запустить сервис, выполнив в терминале следующую команду:
```shell script
sudo systemctl start {service_name}
```
А так же включить сервис в автозапуск, выполнив в терминале слледующую команду:
```shell script
sudo systemctl enable {service_name}
```

## 4. Тестирование сервиса
|**[ВАЖНО\]**| **Не запускайте тесты на машине, где запущена рабочая версия сервиса!**| **[ВАЖНО\]**|
|:---:|:---:|:---:|
|**[ВАЖНО\]**| **Тесты ожидают, что и они и сервис будут работать с чистой базой данных.** |**[ВАЖНО\]**|
|**[ВАЖНО\]**| **По завершении тесты удаляют все таблицы, созданные в базе данных.**| **[ВАЖНО\]**|
|**[ВАЖНО\]**| **Запуск тестов на машине, где запущена рабочая версия сервиса может привести к сбоям в его работе.**| **[ВАЖНО\]**|
---
Для тестирования необходимо запустить сервис локально, как это описано в разделе [3.1](https://github.com/dmitriev-z/backend_yandex#31-запуск-сервиса-локально).

---
Перед тестированием необходимо убедиться, что базы данных `yandexbackend` не существует.  
Для этого необходимо перейти в shell MongoDB, выполнив в терминале команду:
```shell script
mongo
```
Откроется shell MongoDB. В нем выполните команду:
```shell script
show dbs
```
Если в списке баз данных присутствует `yandexbackend`, то необходимо удалить эту базу данных.  
Если база данных `yandexbackend` отсутствует в списке существующих баз данных, то можно закрыть shell MongoBB, выполнив команду:
```shell script
quit()
```
Для удаления базы данных `yandexbackend` выполните следующие команды:
```shell script
use yandexbackend
db.dropDatabase()
```
---

Для запуска тестов из корневой директории сервиса выполните в терминале следующую команду:
```shell script
pytest tests/test_service.py -v
```
Для запуска тестов из директории `/tests` выполните в терминале следующую команду:
```shell script
pytest test_service.py -v
```
Для тестов API используется баблиотека `requests`.  
По умолчанию тесты будут отправлять запросы по адресу `http://127.0.0.1:5000/{path}`.
Если вы запустили сервис на порту, отличном от `5000`, то для этого предусмотрен аргумент `--service-address`.  
Чтобы тесты отправляли запросы по другому адресу, запустите тесты, выполнив в терминале следующую команду:
```shell script
pytest test_service.py --service-address 127.0.0.1:{port}
```
Где `{port}` - порт, на котором запущен сервис.


[CHANGELOG]: ./CHANGELOG.md
[version-badge]: https://img.shields.io/badge/version-4.0.0-blue.svg
