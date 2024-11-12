# PyEnv
```
sudo apt update
sudo apt upgrade
sudo apt install -y git openssl libssl-dev libbz2-dev libreadline-dev libsqlite3-dev
git clone https://github.com/yyuu/pyenv.git ~/.pyenv

sudo vi ~/.bash_profile
以下書き込み
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
以上

source ~/.bash_profile
pyenv --version

pyenv install --list
pyenv install 3.12.2
pyenv global 3.12.2
```
