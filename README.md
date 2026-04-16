# Prototype: AI-gedreven Aanvraagverwerking

Dit project implementeert een end-to-end oplossing voor het verwerken van burgeraanvragen met AI-ondersteuning, fairness-checks en audit-logging.

## Architectuur

- **n8n**: Workflow-orkestratie voor aanvraagflow.
- **FastAPI API**: Backend voor validatie, pseudonimisering, beleid, AI, fairness-check.
- **PostgreSQL**: Audit-database voor logging.
- **Docker Compose**: Complete setup.

## Services

- **n8n**: Workflow automation (http://localhost:5678)
- **API**: FastAPI backend (http://localhost:8000)
- **Frontend**: Simpel HTML form (http://localhost:8080)
- **Audit DB**: PostgreSQL voor logs (localhost:5433)
- **N8N DB**: PostgreSQL voor n8n (localhost:5432)

## Installatie

```bash
# Clone repo
git clone <repo>
cd N8N

# Start alle services
docker-compose up --build -d

# API health check
curl http://localhost:8000/docs

# Stop services
docker-compose down
```

## Frontend
Open http://localhost:8080 voor het formulier. Het stuurt requests naar de n8n webhook, die de API aanroept.

## N8N Workflow
De n8n workflow orkestreert: Webhook → API call → Response.

## Workflow

1. Aanvraag ontvangen via webhook/API
2. Validatie en data minimalisatie
3. Pseudonimisering (citizenId → token)
4. Beleid ophalen
5. AI-service aanroepen voor voorstel
6. Fairness-check
7. Beslissing: auto/manual/rejected
8. Transparant bericht aan burger
9. Audit logging

## Testcases

- Laag risico: Neutrale aanvraag → auto bericht
- Hoog risico: Ernst=hoog + complex → manual review
- Fairness: Verboden term → flag + review
- Validatie: consentAI=false → error

## BPMN Diagram

(Beschrijving: Start → Validatie → Pseudonimisering → Beleid → AI → Fairness → Beslissing → Bericht → Log → End)

## Prompt Charter

Zie `docs/prompt_charter.md` voor AI-regels.
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
