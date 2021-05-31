def get_deal_result(deal_time):
    print('Получаю результат сделки WIN')
    return 'WIN'


def make_deal(option, prognosis, summ, deal_time):
    print('Открываю сделку {option} {prog} {summ} р.\n Время: {tm}'.format(
        option=option,
        prog=prognosis,
        summ=summ,
        tm=deal_time.strftime('%H:%M')
    ))
