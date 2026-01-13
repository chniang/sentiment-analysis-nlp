FROM python:3.11-slim

WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY app.py .
COPY assets ./assets
COPY data ./data
COPY models ./models
COPY utils ./utils

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger les ressources NLTK nécessaires
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('brown'); nltk.download('stopwords')"

# Exposer le port
EXPOSE 8501

# Lancer l'application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
