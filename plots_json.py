from datetime import datetime

import matplotlib.pyplot as plt
import json


# Функция получения данных из json-файла
def get_data_from_json(filename):
    with open(filename, 'r') as file:
        file_data = json.load(file)

    return file_data


def create_plots(plots_data_lists):
    # Создание графиков для отрисовки данных
    fig, axs = plt.subplots(1, 2, figsize=(15,6)) # Получим окно с 1 колонкой и 2 столбцами графиков

    # fig - окно, в котором будут отрисовываться графики
    # axs содержит в себе список графиков для отрисовки на них значений

    # Задание набора точек для отрисовки
    # Первый аргумент - список значений по оси X, второй аргумент - по оси Y
    axs[0].plot(plots_data_lists['date'], plots_data_lists['motion'])
    
    # Задание лейблов для осей и графика
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Motion level')
    axs[0].set_title('Motion')

    # Формирование гистограммы
    axs[1].hist(plots_data_lists['sound'])
    axs[1].set_xlabel('Sound level')
    axs[1].set_ylabel('Count')
    axs[1].set_title('Sound')

    return fig, axs


def main():
    plots_data_lists = {
        'motion': [],
        'sound': [],
        'date': [],
        'temperature': [],
        'power': []
    }

    json_data = get_data_from_json("data.json")

    # Заполнение списков с данными, с преобразованием типов
    for json_dict in json_data:
        plots_data_lists['motion'].append(int(json_dict.get('motion')))
        plots_data_lists['date'].append(datetime.fromisoformat(json_dict.get('date')))
        plots_data_lists['sound'].append(float(json_dict.get('sound')))
        plots_data_lists['power'].append(float(json_dict.get('power')))
        plots_data_lists['temperature'].append(float(json_dict.get('temperature')))

    fig, axs = create_plots(plots_data_lists)

    plt.show()


if __name__ == "__main__":
    main()
