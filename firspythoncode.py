num = int(input())
print('Цифра в позиции тысяч равна', num//1000)
print('Цифра в позиции сотен равна', num%1000//100)
print('Цифра в позиции десятков равна', num%100//10)
print('Цифра в позиции единиц равна', num%10)
