
При возвращении:
1. сделать окна статистики: количество сущностей ползучий график + цифра 
2. Писать над сущностями их имена 
3. Пауза и инспекция при наводе мышки 
5. Все оптимизации которые вынесены в тудушки, научиться анализировать в профайлере + засечь на каком уровне сущностей начинаются лаги и после оптимизауий посмотреть насколько помогает 
6. Проблема с ускорением обучения остра, сильные лаги в процессе визуализации. 
4. Рефакторинг зависимостей и циркулярных импортов

Задачи: 
1. Натренировать существо в синг моде, максимизировать продолжительность жизни. После визуализировать это в визуалайзере. 
2. Сделать так чтоб за тренировкой одного существа можно было наблюдать.
3. Пункт 2 только множество существ одновременно. Проработать вопрос размножения, расширения observation и action_space
-----I AM here ----
4. Добавить хищников. Сделать им другие movements и другие observation.
5. Оттренировать отдельного хищника в синг моде и визуализировать. Тоже самое что с травоядными, только травоядное уже натренировано. 
6. Запустить в визуализации оттренированого хищника и пару травоядных, посмотреть что будет. 
7. Тренировка хищников и травоядных одновременно. 
8. Визуализация тренировки хищников и травоядных одновременно
9. Вживить память, не ограничиваться тем что сущность видит в текущий момент, запоминать что она видела до этого.
10. сделать более хитрый механизм того как будет восстаналиваться еда, ввести в окружение переменную цикла, и пусть еда восстаналивается каждые N циклов 
11. Поработать с рендерингом, писать количество жизней на сущности, ее имя и родителя 
12. Подумать над неймнгом родителей и детей чтоб потом было просто прослеживать родословну
13. переопределить PreyEnv и сделать метод рендер активным через композицию, для того чтоб не рендерить реализовать пустой класс
14. реализовать командную строку 
15. написать ридми 
16. сделать здоровье ребенка рандомным, +- 3 мб от здоровья родителя 
17. Исследовать шум весов при рождении ребенка и наследствии, чтоб не напрямую мозг родителя 
18. Доработать вывод статистики по окончанию игры. 
19. Доработать отображение статистики в отдельном окне по ходу игры 

(!) Идея для резолва Live и train режима в один: возможно стоит на уровне сущности сетить следующее движение, и при движении в самой сущности есть ли движение 
которое задано из вне, и если да, то тогда отдавать его, а если нет то тогда рожать движение самому из брейн


Новое решение с множеством сущностей: 
1. Переходим в режим где сущность опрашивается окружением. Причем каждой сущности инитим модель РРО. 
2. Реализовать рождение. Помимо опроса сущностей о следующем ходе окружение будет опрашивать травоядных о рождении. 
При рождении уменьшается health. Сделать параметром при ините порог при котором происходит рождение. При рождении 
ворачивается новая модель, сущность мозга, которая имеет веса родительской модели, и окружение инитит новую сущность 
рандомно рядом с родителем. После они начиают существовать вместе.
3. Предусмотреть в переводчике окружений момент когда травоядные видят других травоядных (или скорее None) просто 
говорим что в ту область ходить нельзя.
4. уменьшить количество батчей в одной цикле обучения с 2000 до 100, если надо то сделать патч либы, возможно вынести 
эту переменную в сетап какой то, где будет настройки количества шагов обучения после каждого успешного шага
6. параметризироватьчерез сетап скорость обучения, количество эпизодов с таймстемпе и количество таймстепмов
8. Делать обучение моделек не после каждого шага, а после N шагов или после неудачных
   ----- i AM HERE - 
5. На каждом степе сущность обучается 1 цикл. Сущность имеет ссылку на енв. Сущность обучается в тех же условиях 
   (количество еды, хищников и травоядных) в котором щас находится енв.
7. возможно параметризировать цвет сущности через сетап 

