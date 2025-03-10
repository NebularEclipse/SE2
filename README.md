# SE2

---

## Create a virtual environment named venv

```bash
python -m venv venv
```

---

## Activate the virtual environment

### Windows
```PowerShell
./venv/Scripts/activate
```

### Linux
```bash
source venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Initialize database

```bash
flask --app app init-db
```

---

## Run app

### Debug mode
```bash
flask --app app run --debug
```
Remove the debug if you're not debugging