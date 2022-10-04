from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN


def initialize_vpn():
    initialize_VPN(
        save=1,
        area_input=["random countries europe 25"],
        skip_settings=1,
    )
    rotate_VPN()


def terminate_vpn():
    terminate_VPN()
