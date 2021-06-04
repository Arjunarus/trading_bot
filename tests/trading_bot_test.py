import os
import unittest

# Workaround for github tests
if os.name == 'linux' and os.environ.get('DISPLAY') is None:
    os.environ['DISPLAY'] = ':0.0'
    
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
