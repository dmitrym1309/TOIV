from datetime import datetime
import matplotlib.pyplot as plt
import json
from collections import Counter
from typing import List, Dict, Any, Optional

# ---- Настройки по умолчанию (можно менять только это) -----------------------
JSON_PATH = "data.json"

# Что рисуем: какое поле каким типом графика
PLOT_FIELDS = {
    "bar": "motion",           # столбцы
    "line": "temperature",     # линия
    "pie": "voltage vent"      # круговая диаграмма
}

# Сколько знаков округлять для категорий в pie (для чисел)
PIE_ROUND_DIGITS = 2
# -----------------------------------------------------------------------------

def load_json_array(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Ожидался JSON-массив записей.")
    return data

def detect_time_key(rec: Dict[str, Any]) -> Optional[str]:
    for k in rec.keys():
        lk = k.lower()
        if lk in ("time", "date", "timestamp"):
            return k
    return None

def parse_time(s: str) -> Optional[datetime]:
    # Пытаемся ISO; если не вышло — общие форматы
    try:
        return datetime.fromisoformat(s)
    except Exception:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None

def to_float_or_none(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return None

def series_from_records(records: List[Dict[str, Any]], key: str) -> List[Any]:
    """Возвращает список значений по ключу (может быть числовым/строковым)."""
    vals = []
    for r in records:
        vals.append(r.get(key))
    return vals

def numeric_series(records: List[Dict[str, Any]], key: str) -> List[Optional[float]]:
    """Список чисел (или None, если не превратилось)."""
    vals = []
    for r in records:
        vals.append(to_float_or_none(r.get(key)))
    return vals

def build_x_axis(records: List[Dict[str, Any]]) -> List[Any]:
    """Время (если есть и парсится), иначе индекс измерения."""
    if not records:
        return []
    time_key = detect_time_key(records[0])
    if time_key is None:
        return list(range(len(records)))
    xs = []
    for r in records:
        t = r.get(time_key)
        dt = parse_time(str(t)) if t is not None else None
        xs.append(dt if dt else None)
    # если не смогли распарсить ни одной метки — индексы
    if all(v is None for v in xs):
        return list(range(len(records)))
    # заменяем None на предыдущие/индексы — для matplotlib это допустимо,
    # но аккуратнее заменить на индекс
    return [v if v is not None else i for i, v in enumerate(xs)]

def pick_existing_key(records: List[Dict[str, Any]], preferred: str) -> Optional[str]:
    """Если preferred отсутствует, вернуть первый числовой ключ в записи (кроме служебных)."""
    if records and preferred in records[0]:
        return preferred
    if not records:
        return None
    # ищем числовое поле
    for k, v in records[0].items():
        if k.lower() in ("time", "date", "timestamp", "number"):
            continue
        if to_float_or_none(v) is not None:
            return k
    # иначе любой, кроме служебных
    for k in records[0].keys():
        if k.lower() not in ("time", "date", "timestamp"):
            return k
    return None

def prepare_pie_labels(values: List[Any], round_digits: int) -> Dict[str, int]:
    """Строим распределение для pie. Числа округляем, прочее берём как категории."""
    labels = []
    for v in values:
        num = to_float_or_none(v)
        if num is not None:
            labels.append(f"{round(num, round_digits)}")
        else:
            labels.append(str(v))
    return dict(Counter(labels))

def create_plots(records: List[Dict[str, Any]], plot_fields: Dict[str, str]):
    if not records:
        raise ValueError("Нет данных для визуализации.")

    # Уточним реальные ключи (если их переименовали в JSON)
    bar_key = pick_existing_key(records, plot_fields.get("bar", ""))
    line_key = pick_existing_key(records, plot_fields.get("line", ""))
    pie_key = pick_existing_key(records, plot_fields.get("pie", ""))

    # Оси X
    xs = build_x_axis(records)

    # --- подготавливаем данные ---
    bar_vals = numeric_series(records, bar_key) if bar_key else []
    line_vals = numeric_series(records, line_key) if line_key else []
    pie_vals = series_from_records(records, pie_key) if pie_key else []

    # --- Рисуем ---
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    # 1) Столбцы
    axs[0].bar(range(len(bar_vals)), [v if v is not None else 0 for v in bar_vals])
    axs[0].set_xlabel('Номер измерения' if isinstance(xs[0], int) else 'Время')
    axs[0].set_ylabel(bar_key if bar_key else '')
    axs[0].set_title((bar_key or 'bar').upper())

    # 2) Линия
    axs[1].plot(xs, [v if v is not None else float('nan') for v in line_vals])
    axs[1].set_xlabel('Номер измерения' if isinstance(xs[0], int) else 'Время')
    axs[1].set_ylabel(line_key if line_key else '')
    axs[1].set_title(line_key.capitalize() if line_key else 'Line')

    # 3) Круговая
    dist = prepare_pie_labels(pie_vals, PIE_ROUND_DIGITS)
    if dist:
        axs[2].pie(list(dist.values()), labels=list(dist.keys()), autopct='%1.1f%%')
    axs[2].set_title(f'Распределение: {pie_key}' if pie_key else 'Распределение')

    plt.tight_layout()
    return fig, axs

def main():
    records = load_json_array(JSON_PATH)
    create_plots(records, PLOT_FIELDS)
    plt.show()

if __name__ == "__main__":
    main()
