class Config(object):
    DEBUG = False

class ProductionConfig(Config):
    pass

class StagingConfig(Config):
    DEBUG = True


