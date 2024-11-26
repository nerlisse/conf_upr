import yaml
import subprocess
import sys
from collections import defaultdict
import os
import requests
import gzip

class DependencyVisualizer:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.package = self.config["package"]
        self.repo_url = self.config["repo_url"]
        self.visualizer_path = self.config["visualizer_path"]
        self.dependencies = defaultdict(list)

    #функция загрузки yaml-файла
    def load_config(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    #функция загрузки списка пакетов и зависимостей из репозитория
    def load_data(self):
           response = requests.get(self.repo_url, stream=True)
           if response.status_code != 200:
               print(f"error fetching package list from {self.repo_url}", file=sys.stderr)
               sys.exit(1)

            #распаковка gzip и парсинг файла
           package_data = {}
           f = gzip.open(response.raw, encoding="utf-8", mode="rt")
           #проходим по каждой строке
           for line in f:
               line = line.strip()
               if line.startswith("Package:"):
                   #рассмотрение текущего пакета
                   current_package = line.split(":", 1)[1].strip()
               elif line.startswith("Depends:") and current_package:
                   #зависимости текущего пакета
                   depends_raw = line.split(":", 1)[1].strip()
                   dependencies = [
                       dep.split("|")[0].strip().split()[0].strip()  #убираем альтернативные зависимости
                       for dep in depends_raw.split(",")
                   ]
                   package_data[current_package] = dependencies
           return package_data


    #функция получения всех зависимостей необходимого пакетв
    def build_dependency_graph(self):
        metadata = self.load_data()
        visited = set()
        queue = [self.package] #очередь на определение зависимостей пакетов

        while queue:
            #удаляем из очереди первый элемент и проверяем, определяли ли для него зависимость
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            if current in metadata:
                dependencies = metadata[current]
                self.dependencies[current] = dependencies
                #добавляем все зависимые пакеты в очередь
                for dep in dependencies:
                    if dep not in visited:
                        queue.append(dep)

    #функция преобразования списка зависимостей в синтаксис диаграммы mermaid
    def generate_mermaid_diagram(self):
        lines = ["graph TD"] #определяем диаграмму mermaid сверху-вниз
        #зпаисываем каждую зависимость в lines
        for package, deps in self.dependencies.items():
            for dep in deps:
                lines.append(f"    {package} --> {dep}")
        return "\n".join(lines) #объединяем и возвращаем

    #функция генерации изображения
    def visualize(self, output_path="graph.png"):
        mermaid_content = self.generate_mermaid_diagram()
        print(mermaid_content)
        #записываем во временный файл содержимое диаграммы
        temp_file = "temp.mmd"
        with open(temp_file, "w") as f:
            f.write(mermaid_content)

        #вызов инструмента mmdc для генерации изображения
        try:
            subprocess.run(
                [self.visualizer_path, "-i", temp_file, "-o", output_path],
                check=True
            )
            print(f"graph generated at {output_path}")
            os.startfile(output_path)
        finally:
            os.remove(temp_file)  #удаление временного файла


if __name__ == "__main__":
    config_path = "config/config.yaml"
    visualizer = DependencyVisualizer(config_path)
    visualizer.build_dependency_graph()
    visualizer.visualize()
