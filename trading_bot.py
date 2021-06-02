from telethon import TelegramClient, events
import datetime
import logging
import os
import pytz
import re
import sys
import traceback
from apscheduler.schedulers.background import BackgroundScheduler

from broker_manager_gui import BrokerManagerGui, BrokerManagerInterface

BOT_DESCRIPTORS_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'signal_bot_descriptors.json')

# Initial values
logger = logging.getLogger('pyFinance')


def parse_signal(signal_text):
    signal_lines = signal_text.split('\n')
    if len(signal_lines) < 2:
        # Ожидаем как минимум 2 строки, иначе это не сигнал
        return

    option = signal_lines[0][:6]
    if option not in BrokerManagerInterface.OPTION_LIST:
        # Если не нашли известный нам опцион, значит это не сигнал
        return
    
    pattern = r'(вверх|вниз)до(\d{2}.\d{2})мск'
    m = re.match(pattern, signal_lines[1].replace(' ', '').lower())
    if m is None:
        # Если вторая строка не соответствует шаблону, значит это не сигнал
        return

    prognosis = m.group(1)
    deal_time_str = m.group(2)
    deal_time = datetime.datetime.strptime(deal_time_str, '%H.%M').time()
    return option, prognosis, deal_time


def get_summ(init_summ, step):
    return int(init_summ * (2.2 ** (step - 1)))


class TradingBot:
    def __init__(
            self,
            init_summ,
            step,
            broker_manager,
            save_state_file_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'session.sav')
    ):
        self.init_summ = init_summ
        self.step = step
        self.broker_manager = broker_manager
        self.save_state_file_path = save_state_file_path
        self.is_deal = False
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def save_state(self):
        with open(self.save_state_file_path, 'w') as sav:
            sav.write("{} {}".format(self.step, self.init_summ))

        logger.debug("Saved to {}".format(self.save_state_file_path))

    def load_state(self):
        if not os.path.isfile(self.save_state_file_path):
            logger.error("Save state {} is not exists".format(self.save_state_file_path))
            return

        with open(self.save_state_file_path, 'r') as sav:
            content = sav.read()
        self.step, self.init_summ = (int(x) for x in content.split())

        logger.debug("Loaded from {}".format(self.save_state_file_path))
        logger.debug('step = {}'.format(self.step))
        logger.debug('init_summ = {}'.format(self.init_summ))

    def start_deal(self, option, prognosis, deal_time):
        summ = get_summ(self.init_summ, self.step)
        logger.info('Сумма: {}'.format(summ))
        self.broker_manager.make_deal(option, prognosis, summ, deal_time)
        self.is_deal = True

    def finish_deal(self):
        result = self.broker_manager.get_deal_result()

        logger.info('Got result: %s', result)
        if result == 'LOSE':
            self.step += 1
        elif result == 'WIN':
            self.step = 1
        else:
            logger.error('Unknown result: {}'.format(result))

        self.is_deal = False
        self.save_state()

    def message_process(self, message_text, message_date):
        logger.info('')
        logger.info('Got message')
        logger.debug(message_text)
        logger.info(message_date.strftime('Message date: %d-%m-%Y %H:%M'))

        try:
            signal = parse_signal(message_text)
            if signal is None:
                logger.info('Message is not a signal, skip.')
                return

            option, prognosis, deal_time = signal

            logger.info('Получен сигнал: {opt} {prog} до {tm}'.format(
                opt=option,
                prog=prognosis,
                tm=deal_time.strftime('%H.%M')
            ))

            if self.is_deal:
                logger.info('Deal is not finished yet, skip new signal.')
                return

            self.start_deal(option, prognosis, deal_time)

            # Set up timer on finish job
            msk_tz = pytz.timezone('Europe/Moscow')
            now_date = datetime.datetime.now(msk_tz)
            finish_datetime = msk_tz.localize(
                datetime.datetime(
                    now_date.year,
                    now_date.month,
                    now_date.day,
                    deal_time.hour,
                    deal_time.minute
                )
            )
            if deal_time.hour in [0, 1]:
                finish_datetime += datetime.timedelta(days=1)
            finish_datetime = finish_datetime.astimezone()

            logger.debug("finish_datetime={}".format(finish_datetime))

            self.scheduler.add_job(self.finish_deal, 'date', run_date=finish_datetime)

        except Exception as err:
            logger.error("Ошибка: {}\n".format(err))
            traceback.print_exc(file=sys.stdout)


def setup_logging():
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
    setup_logging()

    # Get telephone number, api_id and api_hash from command line
    number, api_id, api_hash, bot_descriptor_name, *rest = sys.argv[1:]

    config = rest[0] if len(rest) > 0 else 'broker_manager_gui_nick_config.json'
    trading_bot = TradingBot(init_summ=50, step=1, broker_manager=BrokerManagerGui(config_file=config))
    trading_bot.load_state()

    client = TelegramClient(number, api_id, api_hash)

    @client.on(events.NewMessage(chats='Scrooge Club'))  # создает событие, срабатывающее при появлении нового сообщения
    async def normal_handler(event):
        message = event.message.to_dict()
        trading_bot.message_process(message['message'], message['date'])

    client.start()
    logger.info('Клиент запущен, бот активен.')
    client.run_until_disconnected()


if __name__ == '__main__':
    main()
