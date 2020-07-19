## Начало работы

### Установить зависимости
Открыть в QGis консоль Python, ввести

```
subprocess.check_call([sys.executable, "-m", "pip", "install",  'pandas', 'scipy', 'geojsoncontour'])
```

### Установить расширение

#### 1 способ
```
git clone https://github.com/shtirlets96/reanalysis_visualization.git
cd reanalysis_visualization
pb_tool deploy
```
#### 2 способ

1) скачать расширение
https://github.com/shtirlets96/reanalysis_visualization/archive/master.zip
2) разархивировать  и скопировать  в 
##### для linux
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
##### для windows
 C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins


#### Далее для обоих способов
1) открыть QGis
2) вкладка Модули => Управление и установка модулей
3) сделать модуль активным