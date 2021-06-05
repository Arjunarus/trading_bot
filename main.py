import datetime
import logging
import os
import sys
from telethon import TelegramClient, events

import trading_bot
from broker_manager_gui import BrokerManagerGui

BOT_DESCRIPTORS_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'signal_bot_descriptors.json')


def setup_logging(logger):
    # Setup main logger
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(datetime.datetime.now().strftime('%Y-%m-%d.log'), 'a', 'utf-8')
    formatter = logging.Formatter('%(asctime)s %(message)s')
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    # Setup telethon logger
    telethon_logger = logging.getLogger('telethon')
    tfh = logging.FileHandler(datetime.datetime.now().strftime('%Y-%m-%d_telethon.log'))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    tfh.setFormatter(formatter)
    telethon_logger.setLevel(logging.DEBUG)
    telethon_logger.addHandler(tfh)


def main():
    # Initial values
    logger = logging.getLogger('pyFinance')
    setup_logging(logger)

    # Get telephone number, api_id and api_hash from command line
    number, api_id, api_hash, bot_descriptor_name, *rest = sys.argv[1:]

    config = rest[0] if len(rest) > 0 else 'broker_manager_gui_nick_config.json'
    t_bot = trading_bot.TradingBot(init_summ=50, step=1, broker_manager=BrokerManagerGui(config_file=config), logger=logger)
    t_bot.load_state()

    client = TelegramClient(number, api_id, api_hash)

    @client.on(events.NewMessage(chats='Scrooge Club'))  # создает событие, срабатывающее при появлении нового сообщения
    async def normal_handler(event):
        message = event.message.to_dict()
        t_bot.message_process(message['message'], message['date'])

    client.start()
    logger.info('Клиент запущен, бот активен.')
    client.run_until_disconnected()


if __name__ == '__main__':
    main()
