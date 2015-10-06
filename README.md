Пакет утилит для разборки (decompiling) и сборки (compiling) *epf*- и *erf*-файлов
===

Что делает
---

При установки пакета в папке скриптов каталога интерпретатора Python создаются исполняемые файлы *decompile1c.exe* и 
*compile1c.exe*, первый используется для разборки *epf*- и *erf*-файлов с помощью 
[v8Reader](https://github.com/xDrivenDevelopment/v8Reader), а второй для их сборки с помощью v8Unpack. 

Пути к платформе 1С:Предприятие 8, сервисной информационной базе, *V8Reader.epf* и *V8Unpack.exe* указывается в файле 
настроек *decompiler1cwrapper.ini*, который сначала ищется в текущем каталоге, а затем в каталоге пользователя 
(в Windows 10 каталог *C:\Users\<Пользователь>*).

Требования
---

- Windows
- Python 3.5
- Платформа 1С:Предприятие 8.3
- Сервисная информационная база (в которой будет запускаться *V8Reader.epf*)
- [v8Reader](https://github.com/xDrivenDevelopment/v8Reader) и в частности *V8Reader.epf*
- v8Unpack \( *V8Unpack.exe* \)