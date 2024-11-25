import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
from homework2.src.Visualizer import DependencyVisualizer
from collections import defaultdict

class TestVisualizer(unittest.TestCase):
    def setUp(self):
        #создаем тестовый конфиг
        self.test_config_path = "test_config.yaml"
        self.test_config = {
            "package": "curl",
            "repo_url": "http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz",
            "visualizer_path": "C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd"
        }
        self.mock_metadata = {
            "curl": ["libcurl4", "openssl"],
            "libcurl4": ["zlib1g"],
            "openssl": [],
            "zlib1g": []
        }

    @patch("builtins.open", new_callable=mock_open, read_data="""
        package: curl
        repo_url: http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz
        visualizer_path: C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd")
    """)
    def test_load_config(self, mock_open_file):
        visualizer = DependencyVisualizer(self.test_config_path)
        self.assertEqual(visualizer.config["package"], "curl")
        self.assertEqual(visualizer.config["repo_url"], "http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz")
        self.assertEqual(visualizer.config["visualizer_path"], "C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd")
        mock_open_file.assert_called_once_with(self.test_config_path, "r")

    @patch("requests.get")
    @patch("gzip.open")
    @patch("builtins.open", new_callable=mock_open, read_data="""
            package: curl
            repo_url: http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz
            visualizer_path: C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd")
        """)
    def test_load_repository_metadata(self, mock_open_file, mock_gzip_open, mock_requests_get):
        #мокаем http-ответ от requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raw = MagicMock()
        mock_requests_get.return_value = mock_response
        #мокаем распакованный gzip файл
        mock_gzip_file = MagicMock()
        mock_gzip_file.__iter__.return_value = iter([
            "Package: curl\n",
            "Depends: libcurl4, openssl\n",
            "Package: libcurl4\n",
            "Depends: zlib1g\n",
            "Package: openssl\n",
            "Package: zlib1g\n"
        ])
        mock_gzip_open.return_value = mock_gzip_file

        #создаем объект визуализатора
        visualizer = DependencyVisualizer("test_config.yaml")
        metadata = visualizer.load_repository_metadata()

        #ожидаемое значение метаданных
        expected_metadata = {
            'curl': ['libcurl4', 'openssl'], 'libcurl4': ['zlib1g']
        }

        #проверяем, что метаданные соответствуют ожидаемым
        self.assertEqual(metadata, expected_metadata)

        #проверяем вызовы заглушек
        mock_requests_get.assert_called_once_with("http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz", stream=True)
        mock_open_file.assert_called_once_with("test_config.yaml", "r")

    from unittest.mock import patch, mock_open

    @patch("builtins.open", new_callable=mock_open, read_data="""
    package: curl
    repo_url: http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz
    visualizer_path: C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd")
    """)
    @patch("Visualizer.DependencyVisualizer.load_repository_metadata")
    def test_build_dependency_graph(mock_load_metadata, mock_open_file):
        #подмена метаданных
        mock_load_metadata.return_value = {
            "curl": ["libcurl4", "openssl"],
            "libcurl4": ["zlib1g"],
            "openssl": [],
            "zlib1g": []
        }

        #создаем объект визуализатора
        visualizer = DependencyVisualizer("test_config.yaml")

        #зпускаем метод построения графа
        visualizer.build_dependency_graph()

        #ожидаемые зависимости
        expected_dependencies = {
            "curl": ["libcurl4", "openssl"],
            "libcurl4": ["zlib1g"],
            "openssl": [],
            "zlib1g": []
        }

        #проверяем, что зависимости построены правильно
        assert visualizer.dependencies == expected_dependencies

        #проверяем, что `open` вызван с правильным путем
        mock_open_file.assert_called_once_with("test_config.yaml", "r")

    from unittest.mock import patch, mock_open

    @patch("builtins.open", new_callable=mock_open, read_data="""
    package: curl
    repo_url: http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz
    visualizer_path: C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd"
    """)
    @patch("visualizer.DependencyVisualizer.load_repository_metadata")
    def test_generate_mermaid_diagram(mock_load_metadata, mock_open_file):
        #подмена метаданных, чтобы избежать сетевых вызовов
        mock_load_metadata.return_value = {
            "curl": ["libcurl4", "openssl"],
            "libcurl4": ["zlib1g"],
            "openssl": [],
            "zlib1g": []
        }

        #создаем объект визуализатора
        visualizer = DependencyVisualizer("test_config.yaml")
        visualizer.build_dependency_graph()

        #ожидаемое содержимое диаграммы Mermaid
        expected_diagram = (
            "graph TD\n"
            "    curl --> libcurl4\n"
            "    curl --> openssl\n"
            "    libcurl4 --> zlib1g\n"
        ).strip()

        #генерируем Mermaid-диаграмму
        diagram = visualizer.generate_mermaid_diagram()

        #гроверяем, что диаграмма совпадает с ожидаемой
        assert diagram.strip() == expected_diagram

        # Проверяем, что заглушка `open` вызвана
        mock_open_file.assert_called_once_with("test_config.yaml", "r")

    @patch("subprocess.run")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.remove")
    def test_visualize(self, mock_remove, mock_open_file, mock_subprocess_run):
        visualizer = DependencyVisualizer(self.test_config_path)
        visualizer.dependencies = self.mock_metadata

        #тестируем, что создается временный файл
        visualizer.visualize(output_path="test_graph.png")

        mock_open_file.assert_called_once_with("temp.mmd", "w")
        mock_subprocess_run.assert_called_once_with(
            ["C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd", "-i", "temp.mmd", "-o", "test_graph.png"],
            check=True
        )
        mock_remove.assert_called_once_with("temp.mmd")
