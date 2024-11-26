import unittest
from unittest.mock import patch, mock_open
import requests
from homework2.src.Visualizer import DependencyVisualizer


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

    @patch("builtins.open", new_callable=mock_open, read_data="""
           package: curl
           repo_url: http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz
           visualizer_path: C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd")
       """)
    def test_load_repository_metadata(self, mock_open_file):
        visualizer = DependencyVisualizer(self.test_config_path)
        response = requests.get(visualizer.config["repo_url"], stream=True)
        assert response.status_code == 200


    @patch("builtins.open", new_callable=mock_open, read_data="""
    package: openssl
    repo_url: http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz
    visualizer_path: C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd")
    """)
    def test_build_dependency_graph(self, mock_open_file):
        visualizer = DependencyVisualizer(self.test_config_path)
        #package_data = visualizer.load_data()
        #зпускаем метод построения графа
        visualizer.build_dependency_graph()

        #ожидаемые зависимости
        expected_dependencies = {
            'openssl': ['libc6', 'libssl1.1'],
             'libc6': ['libgcc-s1', 'libcrypt1'],
             'libssl1.1': ['libc6', 'debconf'],
             'libgcc-s1': ['gcc-10-base', 'libc6'],
             'libcrypt1': ['libc6']

        }

        #проверяем, что зависимости построены правильно
        assert visualizer.dependencies == expected_dependencies



    @patch("builtins.open", new_callable=mock_open, read_data="""
    package: openssl
    repo_url: http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz
    visualizer_path: C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd"
    """)
    def test_generate_mermaid_diagram(self, mock_open_file):
        visualizer = DependencyVisualizer(self.test_config_path)
        visualizer.build_dependency_graph()

        #ожидаемое содержимое диаграммы Mermaid
        expected_diagram = (
        "graph TD\n"
            "    openssl --> libc6\n"
            "    openssl --> libssl1.1\n"
            "    libc6 --> libgcc-s1\n"
            "    libc6 --> libcrypt1\n"
            "    libssl1.1 --> libc6\n"
            "    libssl1.1 --> debconf\n"
            "    libgcc-s1 --> gcc-10-base\n"
            "    libgcc-s1 --> libc6\n"
            "    libcrypt1 --> libc6\n"
        ).strip()

        diagram = visualizer.generate_mermaid_diagram()
        assert diagram.strip() == expected_diagram


    @patch("subprocess.run")
    @patch("builtins.open", new_callable=mock_open, read_data="""
        package: openssl
        repo_url: http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz
        visualizer_path: C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd"
        """)
    @patch("os.remove")
    def test_visualize(self, mock_remove, mock_open_file, mock_subprocess_run):
        visualizer = DependencyVisualizer(self.test_config_path)
        visualizer.dependencies = {
            'openssl': ['libc6', 'libssl1.1'],
             'libc6': ['libgcc-s1', 'libcrypt1'],
             'libssl1.1': ['libc6', 'debconf'],
             'libgcc-s1': ['gcc-10-base', 'libc6'],
             'libcrypt1': ['libc6']

        }

        #тестируем, что создается временный файл
        visualizer.visualize(output_path="graph.png")

        mock_open_file.assert_called_once_with("temp.mmd", "w")
        mock_subprocess_run.assert_called_once_with(
            ["C:/Users/sashk/AppData/Roaming/fnm/node-versions/v22.11.0/installation/mmdc.cmd", "-i", "temp.mmd", "-o", "test_graph.png"],
            check=True
        )
        mock_remove.assert_called_once_with("temp.mmd")
