# TailorTrip AI API
TailorTrip AI backend API

### Endpoints


### Requirements
- python 3
- docker
- docker-compose

### Technology
- Python 3
- Ollama 3.1
- Google Maps


### Setup
##### Navigate to source directory
```
cd src/
```

##### Edit `config.json` base on your needs
```
vi config.json
```
##### Run server
```
poetry run 
```
#### Access on browser
```
http://localhost:3002/docs
```

### Setup with Docker (Alternative)
```
docker-compose -f deployments/docker-compose.yml up -d
```
