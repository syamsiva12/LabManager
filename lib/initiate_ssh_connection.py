import paramiko

class SSHClient:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()

    def connect(self):
        try:
            # Automatically add the server's host key
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the target device
            self.client.connect(self.hostname, username=self.username, password=self.password,timeout=2)
            print(f"Connected to {self.hostname}")

        except Exception as e:
            print(f"Connection failed: {e}")

    def run_execmcd(self, command):
        try:
            # Run the execmcd command
            stdin, stdout, stderr = self.client.exec_command(command)

            # Print the output
            #print("Command Output:")
            #print(stdout.read().decode('utf-8'))
            return stdout.read().decode('utf-8')

        except Exception as e:
            print(f"Command execution failed: {e}")

    def close_connection(self):
        # Close the SSH connection
        self.client.close()
        print(f"Connection to {self.hostname} closed.")