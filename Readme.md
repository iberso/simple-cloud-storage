# Simple Cloud Storage
This project was created to fulfill an individual assignment in a service-oriented architecture course.

we were told to create a simple cloud service where this service has 2 main features:
- File Upload
- File Download

## Technologies Used:
- Python 3
- Flask
- Nameko
- Docker
- Redis
- RabbitMQ
- MySQL

## Service Architecture 
![Architecture-simple-cloud-storage](https://user-images.githubusercontent.com/74914280/175780680-9e857af9-2fb0-4ba7-a57c-1df845839685.png)

## REST API Endpoint

### User Service

```bash
POST /user/register
```

```bash
POST /user/login
```

```bash
POST /user/logout
```

```bash
GET /user/<id_user>
```
### Storage Service
```bash
POST /file/upload
```

```bash
GET /file/download/<id_file>
```

```bash
GET /file/<id_file>/access
```
```bash
GET /file/<id_file>/access
```

```bash 
PUT /file/<id_file>/share/<id_share_to>
```
