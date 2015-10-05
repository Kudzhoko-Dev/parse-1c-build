Утилиты для разборки (decompiling) и сборки (compiling) *epf*- и *erf*-файлов
===

Что делает
---

*epf*- и *erf*-файлы разбираются с помощью [v8Reader](https://github.com/xDrivenDevelopment/v8Reader), а собираются с 
помощью v8Unpack.

Пути к платформе 1С:Предприятие 8, сервисной информационной базе, *V8Reader.epf* и *V8Unpack.exe* указывается в файле 
настроек *decompiler-1c-wrapper.ini*, который сначала ищется в текущем каталоге, а затем в каталоге с утилитами.

Требования
---

- Windows
- Python 3.5
- Платформа 1С:Предприятие 8.3
- Сервисная информационная база (в которой будет запускаться *V8Reader.epf*)
- [v8Reader](https://github.com/xDrivenDevelopment/v8Reader) и в частности *V8Reader.epf*
- v8Unpack \( *V8Unpack.exe* \)

Состав
---

- *decompiler.py* — разборщик *epf*- и *erf*-файлов
- *compiler.py* — сборщик *epf*- и *erf*-файлов
- *decompiler-1c-wrapper.ini.sample* — образец файла с настройками