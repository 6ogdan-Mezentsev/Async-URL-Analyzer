# Async URL Analyzer

Асинхронный сервис для анализа веб-страниц по URL.  
Сервис принимает URL, создаёт задачу анализа, обрабатывает её в отдельном воркере и сохраняет результат в PostgreSQL.\
Статусы выполнения задачи передаются клиенту в реальном времени через WebSocket.\
Проект демонстрирует архитектуру асинхронного backend-сервиса с использованием очередей, worker-процессов и real-time обновлений.

---

# Основные возможности

- Создание задач анализа URL через REST API
- Асинхронная обработка задач в отдельном worker
- Очередь задач на Redis
- Real-time обновления статуса через WebSocket
- Парсинг HTML и вычисление метрик страницы
- Хранение задач и результатов их выполнения в PostgreSQL

---

# Какие метрики анализируются

После обработки страницы сервис сохраняет:

- HTTP статус ответа
- `<title>` страницы
- количество ссылок `<a>`
- количество заголовков `<h1>`
- длину текстового контента страницы

---

# Архитектура

Сервис построен по **асинхронной event-driven архитектуре**.

```
Client
  |
  | REST API
  v
FastAPI
  |
  | записывает Task
  v
PostgreSQL
  |
  | кладёт task_id
  v
Redis Queue (queue:tasks)
  |
  v
Worker
  |
  | анализ страницы
  v
PostgreSQL (TaskResult)
  |
  | публикует статус
  v
Redis Pub/Sub
  |
  v
WebSocket -> Client
```

---

# Компоненты системы

## FastAPI

Основной API сервис.

Функции:

- REST API для создания и получения задач
- WebSocket endpoint для real-time статусов
- валидация URL
- запись задач в PostgreSQL
- отправка задач в Redis очередь

---

## PostgreSQL

Используется для хранения данных о задачах и результатах анализа.

### Таблица `tasks`

| поле | описание |
|-----|----------|
| id | UUID задачи |
| url | анализируемый URL |
| status | статус выполнения |
| created_at | время создания |
| finished_at | время завершения |
| error | текст ошибки |

Статусы задач:

pending - задача создана, но ещё не обработана\
in_progress - задача обрабатывается\
success - задача успешно обработана\
failed - при обработке возникла ошибка\

---

### Таблица `task_result`

| поле | описание |
|-----|----------|
| task_id | UUID задачи |
| http_status | HTTP код ответа |
| title | title страницы |
| links_count | количество ссылок |
| h1_count | количество H1 |
| text_length | длина текста |

## Redis

Используется в двух ролях.

### Очередь задач

`queue:tasks`

Worker читает задачи через: BLPOP queue:tasks

---

### Pub/Sub

Канал статусов:

`tasks:updates:{task_id}`

Через него worker публикует обновления состояния задачи.

---

## Worker

Отдельный процесс, который выполняет обработку задач.

Алгоритм работы:

1. читает `task_id` из Redis queue
2. ставит статус `in_progress`
3. публикует событие в Redis Pub/Sub
4. выполняет HTTP запрос к странице
5. парсит HTML через **BeautifulSoup**
6. вычисляет метрики
7. записывает результат в PostgreSQL
8. публикует финальный статус (`success` или `failed`)

---

# Workflow выполнения задачи

1. Клиент отправляет запрос

    `POST /tasks`

2. API:

   - валидирует URL
   - создаёт запись `Task(status=pending)`
   - кладёт `task_id` в Redis очередь

3. Worker:

   - забирает задачу из очереди
   - анализирует страницу
   - записывает `TaskResult`
   - обновляет статус

4. Клиент:

   - получает статусы через WebSocket  
   или
   - делает запрос в REST API

---

# API

## Создание задачи

`POST /tasks`

### Request

```json
{
  "url": "https://example.com"
}
```

### Response
        
```json
{
  "task_id": "uuid",
  "status": "pending"
}
```

---

## Получить задачу

`GET /tasks/{task_id}`

### Response

```json
{
  "task_id": "uuid",
  "url": "https://example.com",
  "status": "in_progress",
  "created_at": "2026-01-01T12:00:00",
  "finished_at": null,
  "error": null
}
```

---

## Получить результат анализа

`GET /tasks/{task_id}/result`

### Response
```json
{
  "task_id": "uuid",
  "http_status": 200,
  "title": "Example Domain",
  "links_count": 10,
  "h1_count": 1,
  "text_length": 1234
}
```

---

## WebSocket подписка

`WS /ws/tasks/{task_id}`

### Первое сообщение:

```json
{
  "type": "subscribed",
  "task_id": "uuid",
  "channel": "tasks:updates:uuid"
}
```


### Обновления статуса:

```json
{
  "task_id": "uuid",
  "status": "in_progress"
}
```

### Финальный статус:

```json
{
  "task_id": "uuid",
  "status": "success"
}
```

или

```json
{
  "task_id": "uuid",
  "status": "failed"
}
```

---

# Запуск проекта

### Требования

Docker + Docker Compose

### Запуск
`docker compose up --build`

---

# Swagger / Документация FastAPI

FastAPI автоматически генерирует интерактивную документацию:\
Swagger UI: откройте в браузере http://localhost:8000/docs