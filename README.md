# ml-description-based-recommendation-service

Ссылка на google drive, где лежат файлы, весом более 100Mb из папки data и models:
https://drive.google.com/drive/folders/1pdqDUX_1V66NUDnjtJu561CKcsn7RmZB?usp=sharing

Команды для запуска dev сервера:

`docker-compose build `

`docker-compose up`

Swagger:
http://77.234.215.138:18080/ml-description-based-recommendation-service/swagger/

Notion:
https://www.notion.so/ML-Team-1-bb5572fa843147a08befe643211b6b6c

Примеры запросов:

k - количество рекоменадций, выдаваемых в json файле

`http://77.234.215.138:18080/ml-description-based-recommendation-service/predict?wine_id=116&k=10` (рекомендация по id)


`http://77.234.215.138:18080/ml-description-based-recommendation-service/predict?wine_id=116&k=10&description="Вино демонстрирует сложный аромат, сотканный из нот черной смородины, ванили, кокоса, розмарина и гвоздики. Вино обладает щедрым, ярким вкусом с оттенками черешни, кофе и трюфелей, с мягкими танинами и долгим, приятным послевкусием. "Chateau Les Jouberts" Cuvee Prestige, Blaye Cotes de Bordeaux AOC, 2014 — красное сухое вино, созданное из винограда сорта Мерло, который произрастает на виноградниках в аппелласьоне Блай Кот де Бордо на глинисто-гравийных почвах. Сбор урожая проводится лишь по достижении ягод оптимальной спелости, винификация сусла проходит при строго контролируемой температуре в резервуарах из нержавеющей стали. Выдерживается вино 12 месяцев в бочках из французского дуба. Потенциал вина составляет 5 лет."` (рекомендация по description+aroma+taste)
