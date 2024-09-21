# spotdl-web
A wrapper for spotdl with Flask, Celery, redis, and Vue.js. 

## Dev Setup

Install `redis-server`:

```bash
brew install redis
```

Create a virtual environment and install requirements:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

In the `frontend` folder, install the necessary node modules:

```bash
cd frontend
npm i
```

In separate terminals run `redis-server`, `redis-cli monitor`, and `celery`:

```bash
redis-server
redis-cli monitor
celery -A app.celery worker --loglevel=info
```

In another terminal, run the Flask app:

```bash
python app.py
```

In another terminal, change directory into the `frontend` folder and run this command to watch changes and rebuild:

```bash
cd frontend
npx quasar dev
```

This should automatically load in your browser the following URL: [http://localhost:9000](http://localhost:9000)