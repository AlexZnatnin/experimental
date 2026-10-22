c4

#архитектура
C4Context
    title Контекстная диаграмма (C4 Level 1) — Django Ticket System

    Person(user, "Пользователь", "Создаёт тикеты и отслеживает их статус")

    System(ticketSystem, "Django Ticket System", "Небольшое веб-приложение для обработки тикетов")

    System_Ext(pg, "PostgreSQL", "Хранение данных приложений")
    System_Ext(kafka, "Kafka", "Брокер сообщений для асинхронной обработки")
    System_Ext(nginx, "Nginx", "Reverse proxy и точка входа")

    Rel(user, nginx, "Использует HTTPS")
    Rel(nginx, ticketSystem, "Проксирует HTTP-запросы")
    Rel(ticketSystem, pg, "Читает и пишет данные")
    Rel(ticketSystem, kafka, "Публикует и потребляет события")



#контейнеры
C4Container
    title Диаграмма контейнеров (C4 Level 2) — Django Ticket System

    Person(user, "Пользователь", "Создаёт тикеты и отслеживает их статус")

    Container_Boundary(edge, "Edge") {
        Container(nginx, "Nginx", "Reverse proxy", "Терминация TLS, маршрутизация запросов")
    }

    Container_Boundary(app, "Django Application") {
        Container(ticket, "Ticket", "Django app", "Сериализатор и сервис создания тикета, формирует событие")
        Container(outbox, "Outbox", "Django app", "Хранит исходящие события, продьюсер отправляет их в Kafka")
        Container(processing, "Processing", "Django app", "Консьюмер Kafka, хэндлер и релей событий")
        Container(notification, "Notification", "Django app", "Отправка уведомлений пользователям")
        Container(users, "Users", "Django app", "Управление пользователями и аутентификация")
    }

    ContainerDb(pg, "PostgreSQL", "База данных", "Хранит тикеты, пользователей, outbox-события")
    ContainerQueue(kafka, "Kafka", "Брокер сообщений", "Транспорт событий между приложениями")

    Rel(user, nginx, "Использует HTTPS")
    Rel(nginx, ticket, "Проксирует HTTP-запросы")
    Rel(nginx, users, "Проксирует HTTP-запросы")

    Rel(ticket, pg, "Сохраняет тикет и outbox-событие", "SQL")
    Rel(ticket, outbox, "Передаёт событие создания тикета")
    Rel(outbox, pg, "Читает и обновляет outbox-записи", "SQL")
    Rel(outbox, kafka, "Публикует события", "Kafka protocol")

    Rel(kafka, processing, "Доставляет события")
    Rel(processing, pg, "Обновляет статусы и записи", "SQL")
    Rel(processing, notification, "Инициирует уведомление")
    Rel(processing, ticket, "Обновляет состояние тикета")

    Rel(users, pg, "Читает и пишет пользователей", "SQL")
    Rel(notification, pg, "Читает данные для уведомлений", "SQL")