"""
Module for reading configuration files.
"""
import configparser
import os


def read_from_config(filename):
    """
    Reads configuration from the specified file.
    """
    config = configparser.ConfigParser()
    config_path = os.path.join('config', filename)
    config.read(config_path)
    return config


def read_host_interface():
    """
    Reads the host interface from the configuration.
    """
    config = read_from_config('default.ini')
    host_interface = config.get('DEFAULT', 'host_interface')
    return host_interface


def read_payments():
    """
    Reads payments from the configuration.
    """
    config = read_from_config('payments.ini')
    payments = {key: config.getint('DEFAULT', key)
                for key in config['DEFAULT']}
    return payments