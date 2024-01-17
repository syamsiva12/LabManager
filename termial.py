import subprocess
import os

def ssh_gnome_terminal_login(hostname, port, username, password):
    # Command to execute ssh command with sshpass in a new tab of the existing GNOME Terminal
    command = f"bash -c 'sshpass -p \"{password}\" ssh -o StrictHostKeyChecking=no -p {port} {username}@{hostname}; exec bash'"

    # Set the DBUS_SESSION_BUS_ADDRESS environment variable
    dbus_session_bus_address = os.environ.get("DBUS_SESSION_BUS_ADDRESS", None)
    if dbus_session_bus_address is not None:
        env = {"DBUS_SESSION_BUS_ADDRESS": dbus_session_bus_address}
    else:
        env = None

    # Use subprocess to run the command
    subprocess.call(["dbus-send", "--session", "--dest=org.gnome.Terminal", "--type=method_call", "/org/gnome/Terminal", "org.gnome.Terminal.Screen.AddTab", "string:" + command], env=env)

# Replace these values with your SSH server details
hostname = '192.168.107.21'
port = 22  # default SSH port
username = 'root'
password = 'ewn@123'

# Call the function to perform SSH login in a new tab of the existing GNOME Terminal
ssh_gnome_terminal_login(hostname, port, username, password)
