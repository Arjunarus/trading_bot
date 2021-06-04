# Python 3

summa = float(input('введите первоночальную сумму = '))
k = float(input('введите коэффициент мартина = '))
step = int(input('введите кол-во колен = '))
i=1
s=0

for i in range(step):
    a = int(summa * (k ** (i)))
    print('колено №{} = {}'.format(i, a))
    s = s + a
print('общая сумма = ', s)
