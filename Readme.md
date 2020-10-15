# TCP Ping

*запуск доступен только из командной строки
## Примеры использования
***python -m tc_ping google.com -c 10 -p 80***
- отправка 10 пингов на google.com на порт 80

***python -m tc_ping google.com - 0***
- отправка запросов на google.com, пока пользователь не прервет работу программы вручную
и вывод на экран общей статистики

***python -m tc_ping google.com - 1***
- отправка запросов на google.com, пока пользователь не прервет работу программы вручную
и вывод на экран информации по каждому пингу

***подробнее в справке***
- python -m tc_ping -h

#####Автор: Холод Димитрий КБ-201
