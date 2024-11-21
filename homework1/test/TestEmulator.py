import tarfile
import pytest
from homework1.src.ShellEmulator import ShellEmulator

#создание тестовой виртуальной системы
@pytest.fixture
def virtual_fs(tmp_path):
    tar_path = tmp_path / "test_fs.tar"
    with tarfile.open(tar_path, "w") as tar:
        file1 = tmp_path / "file1.txt"
        file1.write_text("line1\nline2\nline1\n")
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        dir2 = tmp_path / "dir2"
        dir2.mkdir()
        file2 = dir2 / "file2.txt"
        file2.write_text("text in file2 WOW")

        tar.add(file1, arcname="file1.txt")
        tar.add(dir1, arcname="dir1")
        tar.add(dir2, arcname="dir2")
        tar.add(file2, arcname="dir2/file2.txt")

    return str(tar_path)


@pytest.fixture
def emulator(virtual_fs): #создание эмулятора для тестирования
    # Создаем эмулятор с тестовой VFS
    config = {"hostname": "test_host", "vfs_path": virtual_fs}
    return ShellEmulator(config)

def test_ls(emulator):
    #тест на содержание директории
    result = emulator.ls()
    assert result == "file1.txt\ndir1\ndir2"

    #содержимое пустой директории
    emulator.change_dir("/dir1")
    result = emulator.ls()
    assert result == ""

    #содержимое вложенной директории
    emulator.change_dir("/dir2")
    result = emulator.ls()
    assert result == "file2.txt"


def test_cd(emulator):
    #переход в существующую директорию
    emulator.change_dir("/dir1")
    assert emulator.current_dir == "/dir1"

    #переход в несуществующую директорию
    result = emulator.change_dir("/nonexistent")
    assert result == "cd: /nonexistent: No such file or directory"

    #переход на уровень выше
    emulator.change_dir("/dir1")
    emulator.change_dir("..")
    assert emulator.current_dir == "/"


def test_exit(emulator):
    #завершение работы
    result = emulator.exit_shell()
    assert result == "exit"

    #выход после выполнения команды
    emulator.ls()
    result = emulator.exit_shell()
    assert result == "exit"

    #выход без выполнения команд
    result = emulator.exit_shell()
    assert result == "exit"


def test_uptime(emulator):
    #формат вывода
    result = emulator.uptime()
    assert "Uptime:" in result

    #время запущенного эмулятор
    import time
    time.sleep(2)
    uptime_seconds = time.time() - emulator.start_time
    result = emulator.uptime()
    assert f"{int(uptime_seconds)}s" in result

    #текущее время в выводе
    current_time = time.strftime("%H:%M:%S", time.localtime())
    result = emulator.uptime()
    assert current_time in result


def test_touch(emulator):
    #создание нового файла
    result = emulator.touch("newfile.txt")
    assert result == "File newfile.txt created"

    #повторное создание файла
    result = emulator.touch("newfile.txt")
    assert result == "File newfile.txt already exists"

    #создание файла в другой директории
    emulator.change_dir("/dir1")
    result = emulator.touch("file_in_dir1.txt")
    assert result == "File file_in_dir1.txt created"


def test_uniq(emulator):
    #уникальные строки в файле
    emulator.vfs["/testfile.txt"] = {
        "is_dir": False, "content": "line1\nline2\nline1"
    }
    result = emulator.uniq("testfile.txt")
    assert result == "line1\nline2" or result == "line2\nline1"

    #уникальные строки в пустом файле
    emulator.vfs["/emptyfile.txt"] = {"is_dir": False, "content": ""}
    result = emulator.uniq("emptyfile.txt")
    assert result == ""

    #отсутствующий файл
    result = emulator.uniq("nofile.txt")
    assert result == "uniq: nofile.txt: No such file or directory"
