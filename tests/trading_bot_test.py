import datetime
import logging
import os
import unittest

import trading_bot
import broker_manager.broker_manager_interface as bm_interface


class BrokerManagerStub(bm_interface.BrokerManagerInterface):
    def get_deal_result(self):
        return 'WIN'

    def make_deal(self, option, prognosis, summ, deal_time):
        return


class TradingBotTest(unittest.TestCase):
    def setUp(self):
        self.descriptor_1 = {
            "name": "Scrooge Club",
            "martingale": True,
            "type": "classic",
            "parser": {
                "lines": 2,
                "pattern": "([a-z]{6})\n(вверх|вниз)до(\\d{2}).(\\d{2})мск",
                "option_index": 1,
                "prognosis_index": 2,
                "hours_index": 3,
                "minutes_index": 4
            }
        }

    def test_get_summ(self):
        # step: summ
        test_data_50 = {
            1: 50,
            2: 110,
            3: 242,
            4: 532,
            5: 1171,
            6: 2576,
            7: 5668,
            8: 12471,
        }

        for step, summ in test_data_50.items():
            real_summ = trading_bot.get_summ(50, step)
            self.assertEqual(real_summ, summ, msg='Incorrect summ calculation for {} step!'.format(step))

        # step: summ
        test_data_300 = {
            1: 300,
            2: 660,
            3: 1452,
            4: 3194,
            5: 7027,
            6: 15460,
            7: 34013,
            8: 74830,
        }

        for step, summ in test_data_300.items():
            real_summ = trading_bot.get_summ(300, step)
            self.assertEqual(real_summ, summ, msg='Incorrect summ calculation for {} step!'.format(step))

    def test_start_finish_deal(self):
        logger = logging.getLogger('pyFinance')
        tbot = trading_bot.TradingBot(
            init_summ=50,
            step=1,
            signal_bot_descriptor=self.descriptor_1,
            broker_manager=BrokerManagerStub(),
            logger=logger,
            save_state_file_path=os.devnull
        )

        self.assertFalse(tbot.is_deal)
        tbot.start_deal(None, None, None)
        self.assertTrue(tbot.is_deal)

        tbot.finish_deal()
        self.assertFalse(tbot.is_deal)

    def test_parse_invalid_signal(self):
        self.assertIsNone(trading_bot.parse_signal('blablabla', self.descriptor_1['parser']))
        self.assertIsNone(trading_bot.parse_signal('EURUSD\nВверх  17.30 мск \n\n', self.descriptor_1['parser']))
        self.assertIsNone(trading_bot.parse_signal('EURUSD Вверх до 17.30 мск', self.descriptor_1['parser']))
        self.assertIsNone(trading_bot.parse_signal('EURUSD\n\nВверх до 17.30 мск', self.descriptor_1['parser']))
        self.assertIsNone(trading_bot.parse_signal('EURUSD+45 000 руб\nAUDUSD+42 700 руб', self.descriptor_1['parser']))

    def test_parse_signal(self):
        signal = trading_bot.parse_signal('\n'.join([
            'EURUSD',
            'Вверх до 17.30 мск ',
            ''
        ]), self.descriptor_1['parser'])
        r_signal = ('EURUSD', 'вверх', datetime.time(hour=17, minute=30))
        self.assertTupleEqual(signal, r_signal)

        signal = trading_bot.parse_signal('\n'.join([
            'EURUSD',
            'Вниз до 18.00 мск',
        ]), self.descriptor_1['parser'])
        r_signal = ('EURUSD', 'вниз', datetime.time(hour=18, minute=00))
        self.assertTupleEqual(signal, r_signal)

        signal = trading_bot.parse_signal('\n'.join([
            'USDJPY',
            'вВеРх ДО23.50 мск'
        ]), self.descriptor_1['parser'])
        r_signal = ('USDJPY', 'вверх', datetime.time(hour=23, minute=50))
        self.assertTupleEqual(signal, r_signal)

        signal = trading_bot.parse_signal('\n'.join([
            'BLABLA',
            'вВеРхДО23.50МСК'
        ]), self.descriptor_1['parser'])
        r_signal = ('BLABLA', 'вверх', datetime.time(hour=23, minute=50))
        self.assertTupleEqual(signal, r_signal)
