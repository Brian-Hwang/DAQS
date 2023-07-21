import argparse
import configparser


def update_payment(vm_name, payment, config_dir):
    payment_config = configparser.ConfigParser()
    payment_config.read(f'{config_dir}/payments.ini')

    if 'DEFAULT' not in payment_config:
        payment_config.add_section('DEFAULT')

    payment_config['DEFAULT'][vm_name] = str(payment)

    with open(f'{config_dir}/payments.ini', 'w') as configfile:
        payment_config.write(configfile)


def main():
    parser = argparse.ArgumentParser(description='Update VM payment.')
    parser.add_argument('vm_name', type=str, help='The name of the VM.')
    parser.add_argument('payment', type=int,
                        help='The new payment for the VM.')
    parser.add_argument('--config_dir', type=str, default='../config',
                        help='The directory of the configuration files.')

    args = parser.parse_args()

    update_payment(args.vm_name, args.payment, args.config_dir)


if __name__ == "__main__":
    main()
