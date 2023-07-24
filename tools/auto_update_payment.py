import configparser
import utils.host_utils as host


def update_payment_config(config_path, default_config_path):
    # Parse the existing configuration file
    config = configparser.ConfigParser()
    config.read(config_path)

    # Parse the default configuration file
    default_config = configparser.ConfigParser()
    default_config.read(default_config_path)
    default_payment = default_config.getint("DEFAULT", "default_payment")

    # Get all VMs
    vms = host.get_vms()

    # Check if each VM has a payment. If not, assign the default payment.
    for vm in vms:
        if not config.has_option("DEFAULT", vm):
            config.set("DEFAULT", vm, str(default_payment))

    # Write the updated configuration back to the file
    with open(config_path, 'w') as configfile:
        config.write(configfile)


# Example usage:
update_payment_config("config/payments.ini", "config/default.ini")
