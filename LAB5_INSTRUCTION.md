# Jenkins + Ansible deployment (Mac -> remote Ubuntu)

Этот проект дополняет лабораторную №4. Старый `ansible/deploy.yml` разворачивал исходники Python через venv/systemd, **не отправлял Docker-образ**. Новый playbook переносит tar-архив образа по SSH, выполняет `docker load`, создаёт том SQLite, заменяет контейнер, проверяет HTTP 200.

## 1. Mac: Ansible

```bash
brew install ansible
ansible --version
```

Убедись, что Jenkins работает от пользователя с Docker Desktop и видит `ansible-playbook`.

## 2. Отдельный сервер

Нужна Ubuntu VM (в Multipass/UTM) или отдельный Ubuntu-хост с SSH и Docker. Для учебной VM можно установить дистрибутивный Docker (для production см. официальный Docker Engine Install):

```bash
sudo apt update
sudo apt install -y openssh-server docker.io python3
sudo systemctl enable --now ssh docker
sudo docker info
uname -m
hostname -I
```

SSH-пользователь для Ansible должен иметь право `sudo` без интерактивного пароля. Типовой пользователь VM Multipass `ubuntu` уже обычно имеет такой доступ. Для отдельного _только учебного_ пользователя `student` на изолированной VM можно создать правило через `sudo visudo -f /etc/sudoers.d/jenkins-ansible` со строкой `student ALL=(ALL) NOPASSWD: ALL` (широкие привилегии, не использовать на production).

## 3. SSH и Jenkins credentials

На Mac:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/jenkins_lab4 -C jenkins-lab4
ssh-copy-id -i ~/.ssh/jenkins_lab4.pub ubuntu@IP_UBUNTU
ssh -i ~/.ssh/jenkins_lab4 ubuntu@IP_UBUNTU 'sudo -n docker info >/dev/null && echo ready'
```

Если `ssh-copy-id` нет, добавь содержимое файла `~/.ssh/jenkins_lab4.pub` в `~/.ssh/authorized_keys` пользователя Ubuntu по консоли VM. **Приватный ключ никогда не добавляй в GitHub.**

Jenkins → Manage Jenkins → Credentials → System → Global credentials → Add Credentials:

- Kind = `SSH Username with private key`
- ID = `lab4-server-ssh`
- Username = `ubuntu` (или фактический SSH-пользователь)
- Private key = содержимое `~/.ssh/jenkins_lab4` (показать `cat ~/.ssh/jenkins_lab4` на своём Mac, не в чате)

Нужен Jenkins плагин **Credentials Binding**.

## 4. GitHub

Из архива скопировать в прежний репозиторий `project-forms` новые `Jenkinsfile`, `ansible/deploy.yml`, `ansible/inventory.ini.example` и `.dockerignore`. `Dockerfile` остаётся прежним. Выполнить:

```bash
git add Jenkinsfile ansible/deploy.yml ansible/inventory.ini.example .dockerignore
git commit -m 'Deploy Docker image to Ubuntu via Jenkins and Ansible'
git push origin main
```

Старый файл `ansible/templates/project-forms.service.j2` больше не используется (можно удалить и закоммитить его удаление). Playbook должен оказаться в GitHub **до первого запуска**.

## 5. Jenkins

Оставь Pipeline script from SCM → GitHub URL → `*/main` → `Jenkinsfile`. После загрузки новой версии Jenkinsfile появится **Build with Parameters** (иногда после одного первичного запуска):

- `DEPLOY_HOST` — реальный IP Ubuntu VM, не пример `192.168.64.10`.
- `TARGET_PLATFORM` — `linux/amd64` для `uname -m` = `x86_64` либо `linux/arm64` для `aarch64` (на Mac с M1 VM чаще `arm64`).

Стадии: Git checkout → Docker build/save → Ansible copy/load/run/HTTP check.

Результат открыть на **http://IP_UBUNTU:8000/**. Проверить на Ubuntu:

```bash
sudo docker ps
sudo docker images | grep project-forms
sudo docker logs project-forms-app
```

При повторном запуске Jenkins заменит контейнер, но Docker volume `project-forms-data` сохранит SQLite.

## Ошибки

- `UNREACHABLE`: IP, SSH и ключ.
- `Missing sudo password`: SSH-пользователю нужно `sudo` без пароля, либо отдельный безопасный механизм become password.
- `ansible-playbook: command not found`: установить Ansible на Mac, где выполняется Jenkins.
- `Credentials not found`: проверить ID `lab4-server-ssh`.
- `exec format error`: выбрать верную TARGET_PLATFORM.
- `port is already allocated`: 8000 занят на Ubuntu.
- Страница не открывается с Mac, хотя Ansible `uri` OK: проверить сеть VM и firewall.

В Jenkinsfile отключена SSH host-key checking **только для изолированной лабораторной VM**. Для рабочей среды проверь fingerprint сервера, добавь его в known_hosts и убери эту настройку.
