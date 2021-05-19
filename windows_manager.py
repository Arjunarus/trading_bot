import logging
import platform
if platform.system() == 'Windows':
    import pygetwindow as gw
else:
    # Workaround for linux system where pygetwindow does not work
    class gw:
        def getWindowsWithTitle(self, _):
            return []


logger = logging.getLogger('pyFinance')


def activate_window(title):
    if platform.system() != 'Windows':
        # Just do nothing on linux
        logger.error('activate_window is not implemented on linux.')
        return

    broker_window_list = gw.getWindowsWithTitle(title)
    if len(broker_window_list) == 0:
        raise RuntimeError('Window "{}" is not found'.format(title))
    broker_window = broker_window_list[0]
    broker_window.activate()
