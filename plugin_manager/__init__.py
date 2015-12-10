try:
    VERSION = __import__('pkg_resources').get_distribution('plugin_manager').version
except Exception as e:
    VERSION = 'unknown'