## 1. How to run the application 

```
docker-compose up
```
*Python version 3.11

## 2. How to open Swagger
```
http://localhost:5001
```
## 3. How to open celery monitoring
```
http://localhost:5555
```
## 4. How to use

#### 4.0 Upload small file and run job
```
curl -X 'POST' \
  'http://localhost:5001/api/calculateDistances/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@sample-geo.csv;type=text/csv'
```
#### or Upload file with 1000 records
```
curl -X 'POST' \
  'http://localhost:5001/api/calculateDistances/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@sample-geo.csv;type=text/csv'
```




#### 4.1 Get job result by task id
```
curl -X 'GET' \
  'http://localhost:5001/api/getResult/fe2e505d-b04d-4caf-90f7-443f6d7407a5' \
  -H 'accept: application/json'
```
