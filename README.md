# Stream processing homework

Сервисное решение из четырех микросервисов: пользователи, биллинг, уведомления и заказы. При создании пользователя автоматически создается счет в биллинге. Заказ списывает средства и сохраняет уведомление с результатом ("письмо счастья" или "письмо горя").

## Сервисы и порты
- user-service: `http://localhost:8000`
- billing-service: `http://localhost:8001`
- notification-service: `http://localhost:8002`
- order-service: `http://localhost:8003`

## Архитектура
Описание вариантов взаимодействия и схема – в [docs/architecture.md](docs/architecture.md). Картинка схемы: [docs/architecture.svg](docs/architecture.svg).

## Запуск локально через Docker Compose
```bash
docker compose up --build
```

## Проверка через Newman

Для проверки сценария ДЗ используется коллекция `postman/stream-processing.postman_collection.json`
c переменной `{{baseUrl}}`, initial value — `http://arch.homework`.

Пример прогона:

```bash
newman run postman/stream-processing.postman_collection.json \
  --env-var baseUrl=http://arch.homework \
  --reporters cli \
  --reporter-cli-show-body \
  --reporter-cli-show-request-headers \
  --reporter-cli-show-response-headers \
  --verbose | tee newman-run.log


Сценарий проходит этапы: создание пользователя с аккаунтом, пополнение, успешный заказ, проверка баланса и уведомлений, неуспешный заказ при недостатке средств и проверка, что баланс не изменился, а уведомление добавилось.

## Helm-установка
Соберите и опубликуйте образ `stream-processing:latest` (значение по умолчанию в values). Затем установите чарта в namespace `stream-processing`:
```bash
helm install stream-processing ./helm -n stream-processing --create-namespace \
  --set image.repository=<ваш-репозиторий> --set image.tag=<ваш-тег>
```

## Ручной запуск без контейнеров
Установите зависимости и запустите сервисы в отдельных терминалах:
```bash
pip install -r requirements.txt
uvicorn services.user_service.main:app --host 0.0.0.0 --port 8000
uvicorn services.billing_service.main:app --host 0.0.0.0 --port 8001
uvicorn services.notification_service.main:app --host 0.0.0.0 --port 8002
uvicorn services.order_service.main:app --host 0.0.0.0 --port 8003
```
