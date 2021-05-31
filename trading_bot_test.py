import datetime
import json
import sys
# Питонье колдунство чтобы подменить импорт в pyFinance_v3_ref
sys.modules['broker_manager_gui'] = __import__('test_data.broker_manager_gui', fromlist=[None])
import trading_bot as bot


def main():
    with open('test_data/result.json', 'r') as mes:
        messages = json.load(mes)

    for msg in messages['messages']:
        text = msg['text']
        date = datetime.datetime.strptime(msg['date'], '%Y-%m-%dT%H:%M:%S')
        bot.message_process(text, date)


if __name__ == '__main__':
    main()
