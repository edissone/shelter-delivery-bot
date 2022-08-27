import os

from src.utils.config import Bot
from src.utils.logger import log

token = os.getenv('TELEGRAM_TOKEN')
if __name__ == '__main__':
    updater = Bot(token).updater
    log.info('Bot created.')
    updater.start_polling(timeout=600, poll_interval=0)
    log.info(f'Bot started polling')
    updater.idle()
