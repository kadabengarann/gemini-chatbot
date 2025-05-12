## Getting Started

### Installation guide

---

### Using Docker (Recommended)

#### Build & Run
```bash
docker compose up -d
```

The app will be accessible at:
```
http://localhost:8080
```

All code changes should be reflected at local.

#### View logs
```bash
docker compose logs -f
```

#### Stop containers
```bash
docker compose down
```

#### Applying Changes
```bash
docker compose down
docker compose up -d
```


---

### Running Locally (Python only)
```bash
pip install -r requirements.txt
cp .env.example .env
python main.py
```