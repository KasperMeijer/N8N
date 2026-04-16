# N8N Docker Setup

Dit project bevat een volledige Docker Compose setup voor n8n met een FastAPI backend.

## Services

- **n8n**: Workflow automation platform (http://localhost:5678)
- **FastAPI API**: Backend service (http://localhost:8000)
- **PostgreSQL**: Database voor n8n

## Starten

```bash
# Start alle services
docker-compose up -d

# Stop services
docker-compose down

# Logs bekijken
docker-compose logs -f n8n
docker-compose logs -f api
```

## Configuratie

### N8N
- **URL**: http://localhost:5678
- **Database**: PostgreSQL lokaal in Docker
- **Workflows**: Geladen vanuit `./n8n/workflow.json`

### FastAPI API
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

### Endpoints
- `POST /validate` - Validatie
- `POST /pseudonymize` - Pseudonimisering
- `POST /policy` - Beleid controle
- `POST /fairness-check` - Eerlijkheidscontrole

## N8N met FastAPI verbinden

1. Open http://localhost:5678
2. Maak een nieuw workflow aan
3. Voeg een "HTTP Request" node toe
4. Stel in:
   - Method: POST
   - URL: http://api:8000/validate (let op: `api` is de service naam in Docker)

## Troubleshooting

### Poorten al in gebruik
Wijzig de poortmapping in docker-compose.yml:
```yaml
ports:
  - "5679:5678"  # n8n op poort 5679
  - "8001:8000"  # API op poort 8001
```

### Database fout
```bash
# Verwijder volumes en start opnieuw
docker-compose down -v
docker-compose up -d
```
