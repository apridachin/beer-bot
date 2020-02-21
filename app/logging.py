import logging


def init_app():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('BeerBot')
    logger.setLevel(logging.DEBUG)
    app_log = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(process)s %(request_id)s %(levelname)s %(name)s %(message)s')
    app_log.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(app_log)


__all__ = ["init_app"]
