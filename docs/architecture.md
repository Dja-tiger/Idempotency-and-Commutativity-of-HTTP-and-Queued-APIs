# Архитектура решения

## Выбранный вариант
Практическая часть реализована в стиле **HTTP orchestration**: сервис заказов управляет сценарием оформления заказа через REST вызовы к сервисам пользователей, биллинга и нотификаций.

![Общая схема](architecture.svg)

## Варианты взаимодействий

### HTTP-only orchestration
```mermaid
sequenceDiagram
    participant Client
    participant User as User API
    participant Billing as Billing API
    participant Order as Order API
    participant Notify as Notification API

    Client->>User: POST /users
    User-->>Billing: POST /accounts
    Client->>Billing: POST /accounts/{id}/deposit
    Client->>Order: POST /orders
    Order->>Billing: POST /accounts/{id}/withdraw
    Billing-->>Order: withdrawn / insufficient
    Order->>Notify: POST /notifications
    Order-->>Client: order status
```

**IDL (OpenAPI фрагменты)**
```yaml
paths:
  /users:
    post:
      summary: Создать пользователя и аккаунт в биллинге
      responses:
        '201': { $ref: '#/components/schemas/User' }
  /accounts/{userId}/withdraw:
    post:
      summary: Списать средства
      responses:
        '200': { $ref: '#/components/schemas/PaymentResult' }
  /notifications:
    post:
      summary: Сохранить уведомление
      responses:
        '201': { $ref: '#/components/schemas/Notification' }
```

### Событийное взаимодействие с брокером для нотификаций
```mermaid
sequenceDiagram
    participant Client
    participant Order as Order API
    participant Billing as Billing API
    participant Broker
    participant Notify as Notification worker

    Client->>Order: POST /orders
    Order->>Billing: POST /withdraw
    Billing-->>Order: result
    Order-->>Broker: publish NotificationRequested
    Notify-->>Broker: subscribe NotificationRequested
    Notify-->>Billing: GET balance (optional)
    Notify-->>Email: deliver
```

**IDL (AsyncAPI фрагмент для брокера)**
```yaml
channels:
  notification.requested:
    publish:
      message:
        name: NotificationRequested
        payload:
          type: object
          properties:
            userId: { type: integer }
            email: { type: string, format: email }
            status: { enum: [confirmed, failed] }
            price: { type: number }
```

### Event Collaboration через брокер
```mermaid
sequenceDiagram
    participant Client
    participant User
    participant Billing
    participant Order
    participant Broker
    participant Notify

    Client->>User: CreateUserCommand
    User-->>Broker: UserCreated
    Billing-->>Broker: subscribe UserCreated
    Billing-->>Broker: AccountCreated
    Client->>Order: PlaceOrderCommand
    Order-->>Broker: OrderPlaced
    Billing-->>Broker: subscribe OrderPlaced
    Billing-->>Broker: PaymentCompleted / PaymentFailed
    Notify-->>Broker: subscribe PaymentCompleted, PaymentFailed
    Notify-->>Broker: NotificationSent
```

**IDL (команды/события)**
```yaml
messages:
  UserCreated:
    payload:
      type: object
      properties:
        userId: { type: integer }
        email: { type: string }
  PaymentFailed:
    payload:
      type: object
      properties:
        orderId: { type: integer }
        reason: { type: string }
```

### Наиболее адекватный вариант
Для учебного решения выбран вариант HTTP orchestration (первый), так как он проще всего поднимается локально без брокера и демонстрирует все требуемые шаги.
