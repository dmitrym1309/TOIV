import pandas as pd
import matplotlib.pyplot as plt

# Читаем данные из CSV
data = pd.read_csv('data.csv')

# Названия колонок (адаптируй под свой CSV)
col1 = 'motion'          # 1-е значение → столбцы
col2 = 'temperature'     # 2-е значение → линия
col3 = 'voltage vent'    # 3-е значение → круговая диаграмма

plt.figure(figsize=(15, 5))  # одно полотно с тремя графиками

# --- 1️⃣ Столбчатая диаграмма ---
plt.subplot(1, 3, 1)
plt.bar(range(len(data[col1])), data[col1])
plt.xlabel('Номер измерения')
plt.ylabel(col1)
plt.title(col1.upper())

# --- 2️⃣ Линейный график ---
plt.subplot(1, 3, 2)
plt.plot(range(len(data[col2])), data[col2])
plt.xlabel('Номер измерения')
plt.ylabel(col2)
plt.title('Температура')

# --- 3️⃣ Круговая диаграмма ---
plt.subplot(1, 3, 3)
value_counts = data[col3].value_counts()
plt.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%')
plt.title('Распределение напряжений')

# --- Общие настройки ---
plt.tight_layout()
plt.show()
