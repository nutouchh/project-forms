# Лабораторная работа №3 — Ansible

Ansible развёртывает приложение из лабораторной №2 в текущей локальной Ubuntu.
Эта Ubuntu одновременно является управляющей машиной и «сервером»

```bash
/usr/bin/sudo.ws --version
```

Если файла нет, один раз установить:

```bash
sudo apt update
sudo apt install -y sudo
```

## 1. Перейти в проект

Все следующие команды выполнять в одной локальной консоли Ubuntu:

```bash
cd ~/projects/project-forms
```

## 2. Проверить inventory

```bash
cat ansible/inventory.ini
```

Файл должен содержать:

```ini
[web]
labserver ansible_connection=local ansible_host=127.0.0.1 ansible_python_interpreter=/usr/bin/python3 ansible_become_exe=/usr/bin/sudo.ws
```

Если нужно изменить файл:

```bash
nano ansible/inventory.ini
```

Сохранить: Ctrl+O → Enter. Выйти: Ctrl+X.

## 3. Проверить Ansible и права

Проверка выполнения задач:

```bash
ansible web -i ansible/inventory.ini -m ansible.builtin.ping
```

Ожидается `SUCCESS` и `"ping": "pong"`.

Проверка повышения прав:

```bash
ansible web -i ansible/inventory.ini -m ansible.builtin.command -a "whoami" --become -K
```

Ввести пароль пользователя student в этой Ubuntu. Ожидается ответ `root`.
Символы пароля при вводе не отображаются. Флаг `-k` не нужен: SSH не используется.

## 4. Проверить синтаксис плейбука

```bash
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml --syntax-check
```

Если ошибок нет, команда выводит имя плейбука.

## 5. Выполнить развёртывание

```bash
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml -K
```

Ввести пароль student. Дождаться завершения.
В итоговом PLAY RECAP должны быть `failed=0` и `unreachable=0`.

Плейбук устанавливает пакеты, копирует код в `/opt/project-forms`, создаёт venv, устанавливает Flask и Gunicorn, настраивает службу и проверяет HTTP 200.

## 6. Проверить службу и приложение

```bash
sudo systemctl status project-forms --no-pager
sudo systemctl is-enabled project-forms
curl --noproxy '*' -I http://127.0.0.1:8000
```

Ожидается: `active (running)`, `enabled`, `HTTP/1.1 200 OK`.
Если просмотр статуса открылся в режиме просмотра, выйти клавишей q.

В браузере Windows открыть:

http://localhost:8000

Создать заявку, открыть её, изменить и удалить тестовую запись.

## 7. Показать повторное выполнение

Создать ещё одну заявку и оставить её в списке. Повторить:

```bash
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml -K
```

Последние сообщения приложения:

```bash
sudo journalctl -u project-forms -n 40 --no-pager
```
