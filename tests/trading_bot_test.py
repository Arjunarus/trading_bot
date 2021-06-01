import datetime
import os
import unittest

import trading_bot


class TradingBotTest(unittest.TestCase):
    def setUp(self):
        trading_bot.step = 1
        trading_bot.init_summ = 50
        trading_bot.SAVE_STATE_FILE_PATH = os.devnull

    def test_get_summ(self):
        trading_bot.init_summ = 50
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
            real_summ = trading_bot.get_summ(step)
            self.assertEqual(real_summ, summ, msg='Incorrect summ calculation for {} step!'.format(step))

        trading_bot.init_summ = 300
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
            real_summ = trading_bot.get_summ(step)
            self.assertEqual(real_summ, summ, msg='Incorrect summ calculation for {} step!'.format(step))

    def test_deal_result_process(self):
        init_step = trading_bot.step
        trading_bot.deal_result_process('LOSE')
        self.assertEqual(trading_bot.step, init_step + 1, msg='LOSE result do not increment the step.')

        trading_bot.step = 10
        trading_bot.deal_result_process('WIN')
        self.assertEqual(trading_bot.step, 1, msg='WIN result should reset step to 1.')

    def test_parse_signal_invalid(self):
        self.assertIsNone(trading_bot.parse_signal('blablabla'))
        self.assertIsNone(trading_bot.parse_signal('EURUSD\nВверх  17.30 мск \n\n'))
        self.assertIsNone(trading_bot.parse_signal('EURUSD Вверх до 17.30 мск'))
        self.assertIsNone(trading_bot.parse_signal('BLABLA\nВверх до 17.30 мск'))
        self.assertIsNone(trading_bot.parse_signal('EURUSD+45 000 руб\nAUDUSD+42 700 руб'))

        # test GBPUSD is absent
        self.assertIsNone(trading_bot.parse_signal('GBPUSD\nВверх до 17.30 мск'))

    def test_parse_signal(self):
        signal = trading_bot.parse_signal('EURUSD\nВверх до 17.30 мск \n\n')
        r_signal = ('EURUSD', 'вверх', datetime.time(hour=17, minute=30))
        self.assertTupleEqual(signal, r_signal)

        signal = trading_bot.parse_signal('EURUSD\nВниз до 18.00 мск')
        r_signal = ('EURUSD', 'вниз', datetime.time(hour=18, minute=00))
        self.assertTupleEqual(signal, r_signal)

        signal = trading_bot.parse_signal('USDJPY\nвВеРх ДО23.50 мск')
        r_signal = ('USDJPY', 'вверх', datetime.time(hour=23, minute=50))
        self.assertTupleEqual(signal, r_signal)

        signal = trading_bot.parse_signal('USDJPY\nвВеРхДО23.50МСК')
        r_signal = ('USDJPY', 'вверх', datetime.time(hour=23, minute=50))
        self.assertTupleEqual(signal, r_signal)
