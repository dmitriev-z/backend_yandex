# Yandex Backend School Task
[![version][version-badge]][CHANGELOG]

REST API сервис для обработки выгрузок данных интернет-магазина подарков.

## Содержание
>1\. [Описание сервиса](https://github.com/dmitriev-z/backend_yandex#1-описание-сервиса)
>>1.1 [Обработчики запросов](https://github.com/dmitriev-z/backend_yandex#11-обработчики-запросов)    
>>>1.1.1 [POST /imports](https://github.com/dmitriev-z/backend_yandex#111-post-imports)  
>>>1.1.2 [PATCH /imports/$import_id/citizens/$citizen_id](https://github.com/dmitriev-z/backend_yandex#112-patch-importsimport_idcitizenscitizen_id)   
>>>1.1.3 [GET /imports/$import_id/citizens](https://github.com/dmitriev-z/backend_yandex#113-get-importsimport_idcitizens)
>>
>>1.2 [Управление сервисом](https://github.com/dmitriev-z/backend_yandex#12-управление-сервисом)
>
>2\. [Установка сервиса](https://github.com/dmitriev-z/backend_yandex#2-установка-сервиса)
>>2.1 [Установка требуемых пакетов](https://github.com/dmitriev-z/backend_yandex#21-установка-требуемых-пакетов)  
>>2.2 [Установка MongoDB Community Edition](https://github.com/dmitriev-z/backend_yandex#22-установка-mongodb-community-edition)  
>>2.3 [Создание виртуального окружения](https://github.com/dmitriev-z/backend_yandex#23-создание-виртуального-окружения)  
>>2.4 [Установка требуемых python библиотек](https://github.com/dmitriev-z/backend_yandex#24-установка-требуемых-python-библиотек)  

## 1. Описание сервиса
Сервис написан на `Python 3.6` и запущен в виртуальной окружении с именем `env`.    
Сервис развернут на виртуальной машине `84.201.156.229` на порту `8080` .  
В качестве хранилища данных используется NoSQL база данных MongoDB Community Edition. База данных развернута на той же виртуальной машине на порту `27017`.

### 1.1. Обработчики запросов
Сервис поддерживает 3 обработчика запросов:

| **№**   | **URL**           | **Method**        | 
|:---:| ------------- |:-------------:| 
| 1   |   `http://84.201.156.229/imports`    | *POST* |
| 2   |   `http://84.201.156.229/imports/$import_id/citizens/$citizen_id`    | *PATCH*     |
| 3   | `http://84.201.156.229/imports/$import_id/citizens` | *GET*      |

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
В случае, если входные данные не прошли валидацию (данные не были переданы, отсутствуют обязательные поля, присутсвуют неописанные поля, неправильное значение поля), сервис вернет ответ `400: Bad Request`.

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

Все требуемые библиотеки описаны в файле `requirements.txt`.  
Для установки требуемых библиотек выполните в терминале следующую команду:
```shell script
sudo pip3 install -r requirements.txt
```

[CHANGELOG]: ./CHANGELOG.md
[version-badge]: https://img.shields.io/badge/version-1.0.4-blue.svg
