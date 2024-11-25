import yaml
import subprocess
import sys
from collections import defaultdict
import os

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

    #функция получения зависимости пакетв
    def get_package_dependencies(self, package):
        try:
            #выполняем команду "apt-cache depends _packagename_"
            result = subprocess.run(
                ["apt-cache", "depends", package],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            dependencies = []
            #проходим по каждой строчке
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("Depends:"):
                    #убираем лишние символы
                    dep = line.split("Depends:")[1].strip()
                    dep = dep.strip('<>')  #удаляем символы < и >
                    dependencies.append(dep)
            return dependencies

        except subprocess.CalledProcessError as e: #ошибка в случае недоступности пакетв
            print(f"error fetching dependencies for {package}: {e}", file=sys.stderr)
            return []

    #функция получения всех зависимостей необходимого пакетв
    def build_dependency_graph(self):
        visited = set()
        queue = [self.package] #очередь на определение зависимостей пакетов

        while queue:
            #удаляем из очереди первый элемент и проверяем, определяли ли для него зависимость
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            #определяем зависимости для этого пакетв
            dependencies = self.get_package_dependencies(current)
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
        #print(mermaid_content)
        #записываем во временный файл содержимое диаграммы
        temp_file = "temp.mmd"
        with open(temp_file, "w") as f:
            f.write(mermaid_content)

        #вызов инструмента mmdc для генерации изображения
        try:
            subprocess.run(
                [self.visualizer_path, "-i", temp_file, "-o", output_path, "--puppeteerConfigFile", "config/pconfig.json"],
                check=True
            )
            print(f"graph generated at {output_path}")
            os.system(f'xdg-open "{output_path}"')
        finally:
            os.remove(temp_file)  #удаление временного файла


if __name__ == "__main__":
    config_path = "config/config.yaml"
    visualizer = DependencyVisualizer(config_path)
    visualizer.build_dependency_graph()
    visualizer.visualize()