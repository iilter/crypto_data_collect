import datetime
import logging
import os
import sys
import traceback


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def log_traceback(ex, ex_traceback=None):
    # logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s %(name)s - %(levelname)s - %(message)s')
    logging.basicConfig(filename='app.log',
                        filemode='a',
                        format='%(asctime)s: %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = traceback.format_exception(ex.__class__, ex, ex.__traceback__)
    tb_text = ''.join(tb_lines)
    logging.exception(tb_text)


def log_error(message):
    logging.basicConfig(filename='app.log',
                        filemode='a',
                        format='%(asctime)s: %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logging.error(message)
