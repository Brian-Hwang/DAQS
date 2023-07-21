import argparse
import configparser


def update_total_bandwidth(total_bandwidth, config_dir):
    config = configparser.ConfigParser()
    config.read(f'{config_dir}/config.ini')

    if 'DEFAULT' not in config:
        config.add_section('DEFAULT')

    config['DEFAULT']['total_bandwidth'] = str(total_bandwidth)

    with open(f'{config_dir}/config.ini', 'w') as configfile:
        config.write(configfile)


def main():
    parser = argparse.ArgumentParser(description='Update total bandwidth.')
    parser.add_argument('total_bandwidth', type=int,
                        help='The new total bandwidth.')
    parser.add_argument('--config_dir', type=str, default='../config',
                        help='The directory of the configuration files.')

    args = parser.parse_args()

    update_total_bandwidth(args.total_bandwidth, args.config_dir)


if __name__ == "__main__":
    main()
