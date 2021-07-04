import datetime
import json
import logging
import os
import sys
from telethon import TelegramClient, events

import trading_bot
from broker_manager.broker_manager_gui import BrokerManagerGui

BOT_DESCRIPTORS_FILE_NAME = 'signal_bot_descriptors.json'
DEFAULT_BROKER_MANAGER_GUI_CONFIG = 'broker_manager_gui_nick_config.json'


def setup_logging(logger):
    if not os.path.isdir("log"):
        os.mkdir("log")

    # Setup main logger
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(os.path.join('log', datetime.datetime.now().strftime('%Y-%m-%d.log')), 'a', 'utf-8')
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
    tfh = logging.FileHandler(os.path.join('log', datetime.datetime.now().strftime('%Y-%m-%d_telethon.log')))
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

    config = rest[0] if len(rest) > 0 else DEFAULT_BROKER_MANAGER_GUI_CONFIG
    bot_descriptors_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), BOT_DESCRIPTORS_FILE_NAME)
    with open(bot_descriptors_file_path, 'r', encoding='utf-8') as desc:
        json_content = json.load(desc)
        signal_bot_descriptor = json_content[bot_descriptor_name]

    t_bot = trading_bot.TradingBot(
        init_summ=50,
        step=1,
        signal_bot_descriptor=signal_bot_descriptor,
        broker_manager=BrokerManagerGui(config_file=config),
        logger=logger
    )
    t_bot.load_state()

    client = TelegramClient(number, api_id, api_hash)

    # Обработчик события получения нового сообщения
    @client.on(events.NewMessage(chats=signal_bot_descriptor['name']))
    async def normal_handler(event):
        message = event.message.to_dict()
        t_bot.message_process(message['message'], message['date'])

    client.start()
    logger.info('Клиент запущен, бот активен.\n')
    client.run_until_disconnected()


if __name__ == '__main__':
    main()
