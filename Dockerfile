# Используем официальный образ Python в качестве основы
FROM python:3.10-slim

# Устанавливаем PostgreSQL клиент и другие необходимые пакеты
RUN apt-get update && apt-get install -y postgresql-client

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Определяем команду для запуска приложения
CMD ["python", "main.py"]
