# Программы для проекта ЕмПолимер

В проекте содержится три программы:

- `empolimer_wifi_arduino` — программа для Arduino UNO считывает данные с реального датчика температуры и влажности DHT11 и отображает их на дисплее Nokia 5110. Параллельно с этим, каждые 3 секунды отправляет значения температуры и влажности в формате строк вида temp:24 и hum:60 по программному последовательному порту (SoftwareSerial) на WiFi-модуль (например, ESP-12F). Это позволяет модулю обновлять значения на веб-странице или публиковать их в MQTT. Основной порт Serial используется для отладки и не влияет на передачу данных.

- `empolimer_wifi_arduino_test` - программа для Arduino UNO имитирует сбор данных с датчиков (например, температуры и влажности) и передаёт их в формате строк вида temp:24.5 и hum:60 по последовательному порту на WiFi-модуль через программный UART (SoftwareSerial). Передача происходит каждые 3 секунды, что позволяет модулю регулярно обновлять значения на веб-странице и публиковать их в MQTT. Основной последовательный порт (Serial) используется только для отладки и не мешает передаче данных.

- `empolimer_wifi_esp` - программа для WiFi модуля, который подключается к Wi-Fi и запускает веб-сервер, отображающий текущие показания температуры и влажности, полученные от Arduino UNO через UART. Каждые 3 секунды браузер автоматически запрашивает новые данные через AJAX, получая их в формате JSON. Одновременно WiFi публикует полученные данные в MQTT-брокер с использованием заданного логина. Веб-страница отображает данные в удобном виде, а обновление происходит без перезагрузки страницы.

В проекте используется Wi-Fi (Troyka-модуль) от [Амперка](https://wiki.amperka.ru/продукты:troyka-wi-fi)

## Подключение WiFi модуля к Arduino UNO

Подключение в режиме работы:

- D8 -> TX (Приём от WiFi модуля)
- D9 -> RX (Передача на WiFi модуль)
- GND -> GND (Общий минус)
- 5V -> V (Питание модуля)

## Загрузка программы на WiFi-модуль

1. Введите в программу данные для подключения к WiFi-сети и MQTT-брокеру

2. Подключите модуль WiFi к Arduino:

![Изображение](/docs/images/upload_schema.png "Установка виртуальной среды")

3. Переведите модуль в режим программирования и запустите загрузку скетча:
    1. Отключите модуль от питания;
    2. Запустите загрузку скетча на плату Generic ESP8266 Module;
    2. Зажмите кнопку `PROG` на модуле;
    3. Подключите к модулю питание;
    4. Отпустите кнопку `PROG`

5. Дождитесь окончания загрузки программы и переподключите питание WiFi-модуля

6. Подключите WiFi-модуль в режим работы (в пины для обмена данными с Arduino Uno)

## MQTT-брокер

В качестве MQTT-брокера используется бесплатный сервис [https://dealgate.ru/](https://dealgate.ru/).

Для работы в сервисе необходимо зарегистрироваться через учётную запись Яндекс и выполнить настройки по [инструкциям](https://dealgate.ru/help/5.html) с сайта (создать устройство и умения с указанными топиками "arduino/temp" и "arduino/hum")

В программу для загрузки на WiFi-модуль необходимо ввести адрес MQTT-cервера, а также username и password из личного кабинета

## Установка библиотек

1. В программе Arduino IDE перейдите в меню: Скетч → Подключить библиотеку → Управлять библиотеками...
2. В открывшемся Менеджере библиотек введите названия в поле поиска и установите библиотеки (со всеми зависимостями):
    - `Adafruit GFX` → для установки "Adafruit GFX Library"
    - `Adafruit PCD8544` → для установки "Adafruit PCD8544 Nokia 5110 LCD library"
    - `DHT sensor library` → для установки "DHT sensor library by Adafruit"