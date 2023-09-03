# Notification Service

## Запуск:

1. Создать файл с переменными окружения на основе .env.example
2. Запустить docker-compose:

```shell
docker-compose up --build  
```

Для организации отправки сообщений используется RabbitMQ<br />
Для отправки сообщений применяется ElasticEmail в качестве SMTP провайдера

Графическое представление и структура проекта:
<img src='https://github.com/fedotovdmitriy14/notifications/blob/master/structure.jpg' />
