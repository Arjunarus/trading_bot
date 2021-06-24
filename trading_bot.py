import datetime
import os
import pytz
import re
import sys
import traceback
from apscheduler.schedulers.background import BackgroundScheduler


def parse_signal(signal_text, parser):
    signal_lines = signal_text.split('\n')
    # Check lines count
    if len(signal_lines) < int(parser['lines']):
        return

    m = re.match(parser['pattern'], signal_text.replace(' ', '').lower())
    # Check if pattern matching
    if m is None:
        return

    option = m.group(parser['option_index']).upper()
    prognosis = m.group(parser['prognosis_index'])
    hours_idx = parser['hours_index']
    deal_hour = 0
    if hours_idx is not None:
        deal_hour = int(m.group(hours_idx))
    deal_minutes = int(m.group(parser['minutes_index']))
    signal_time = datetime.time(hour=deal_hour, minute=deal_minutes)
    return option, prognosis, signal_time


def get_finish_time(signal_time, signal_type):
    if signal_type == 'classic':
        # Классические сигналы для мск пояса
        msk_tz = pytz.timezone('Europe/Moscow')
        now_date = datetime.datetime.now(msk_tz)
        signal_time = msk_tz.localize(
            datetime.datetime(
                now_date.year,
                now_date.month,
                now_date.day,
                signal_time.hour,
                signal_time.minute
            )
        )
        if signal_time.hour in [0, 1]:
            signal_time += datetime.timedelta(days=1)
        finish_time = signal_time.astimezone()

    elif signal_type == 'sprint':
        finish_time = datetime.datetime.now() + datetime.timedelta(hours=signal_time.hour, minutes=signal_time.minute)

    else:
        raise ValueError('Unknown signal type: {}'.format(signal_type))

    return finish_time


def get_summ(init_sum, step):
    return int(init_sum * (2.2 ** (step - 1)))


class TradingBot:
    def __init__(
            self,
            init_summ,
            step,
            signal_bot_descriptor,
            broker_manager,
            logger,
            save_state_file_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'session.sav'),
    ):
        self.init_summ = init_summ
        self.step = step
        self.signal_bot_descriptor = signal_bot_descriptor
        self.broker_manager = broker_manager
        self.logger = logger
        self.save_state_file_path = save_state_file_path
        self.is_deal = False
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def save_state(self):
        with open(self.save_state_file_path, 'w') as sav:
            sav.write("{} {}".format(self.step, self.init_summ))

        self.logger.debug("Saved to {}".format(self.save_state_file_path))

    def load_state(self):
        if not os.path.isfile(self.save_state_file_path):
            self.logger.error("Save state {} is not exists".format(self.save_state_file_path))
            return

        with open(self.save_state_file_path, 'r') as sav:
            content = sav.read()
        self.step, self.init_summ = (int(x) for x in content.split())

        self.logger.debug("Loaded from {}".format(self.save_state_file_path))
        self.logger.debug('step = {}'.format(self.step))
        self.logger.debug('init_summ = {}'.format(self.init_summ))

    def start_deal(self, option, prognosis, finish_time):
        summ = get_summ(self.init_summ, self.step)
        self.logger.info('Сумма: {}'.format(summ))
        self.is_deal = True
        return self.broker_manager.make_deal(option, prognosis, summ, finish_time)

    def finish_deal(self):
        self.is_deal = False

        if not self.signal_bot_descriptor['martingale']:
            # Если нет мартингейла то ниче не надо делать
            return

        result = self.broker_manager.get_deal_result()

        self.logger.info('Got result: %s', result)
        if result == 'LOSE':
            self.step += 1
        elif result == 'WIN':
            self.step = 1
        else:
            self.logger.error('Unknown result: {}'.format(result))

        self.save_state()

    def message_process(self, message_text, message_date):
        self.logger.info('')
        self.logger.info('Got message')
        self.logger.debug(message_text)
        self.logger.info(message_date.strftime('Message date: %d-%m-%Y %H:%M'))

        try:
            signal = parse_signal(message_text, self.signal_bot_descriptor['parser'])
            if signal is None:
                self.logger.info('Message is not a signal, skip.')
                return

            option, prognosis, signal_time = signal
            self.logger.info('Получен сигнал: {opt} {prog} время {tm}'.format(
                opt=option,
                prog=prognosis,
                tm=signal_time.strftime('%H.%M')
            ))

            if option not in self.broker_manager.OPTION_LIST:
                self.logger.info('Unknown option {}, skip.'.format(option))
                return

            if self.is_deal:
                self.logger.info('Deal is not finished yet, skip new signal.')
                return

            finish_time = get_finish_time(signal_time, self.signal_bot_descriptor['type'])
            real_finish_time = self.start_deal(option, prognosis, finish_time)

            # Set up timer on finish job
            self.scheduler.add_job(self.finish_deal, 'date', run_date=real_finish_time)

        except Exception as err:
            self.logger.error("Ошибка: {}\n".format(err))
            traceback.print_exc(file=sys.stdout)
