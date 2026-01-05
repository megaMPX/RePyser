#!/bin/bash

echo "Установка зависимостей Python из requirements.txt..."
pip install -r requirements.txt

echo "Установка pycdc..."
if ! command -v git &> /dev/null
then
    echo "Git не найден. Пожалуйста, установите Git и попробуйте снова."
    exit 1
fi

if ! command -v cmake &> /dev/null
then
    echo "cmake не найден. Пожалуйста, установите 'cmake' и попробуйте снова."
    exit 1
fi

if ! command -v make &> /dev/null
then
    echo "make не найден. Пожалуйста, установите 'build-essential' или 'make' и попробуйте снова."
    exit 1
fi

git clone https://github.com/zrax/pycdc.git
cd pycdc

cmake .
if [ $? -ne 0 ]; then
    echo "Ошибка выполнения cmake для pycdc."
    exit 1
fi

make
if [ $? -ne 0 ]; then
    echo "Ошибка сборки pycdc."
    exit 1
fi

echo "Для установки pycdc в /usr/local/bin/ требуется пароль sudo."
sudo make install
if [ $? -ne 0 ]; then
    echo "Ошибка установки pycdc."
    exit 1
fi

cd ..
rm -rf pycdc

echo "Установка завершена успешно!"
