import paramiko
import datetime as dt
import time
import os


class NodeSshController:
    def __init__(self, ip, username, password):
        print("Initializing SSH controller...")
        self.ip = ip
        self.password = password
        self.username = username
        self.status_ok = True
        self.config = {}

        with open('log_setup.cfg', 'r') as cfg:
            lines = cfg.readlines()
            for line in lines:
                key = line[:line.find('=')]
                try:
                    value = bool(int(line[line.find('=') + 1:]))
                except ValueError:
                    value = line[line.find('=') + 1:]
                self.config[key] = value
            self.verbose = self.config['verbose']
            self.logging = self.config['logging']
            self.logfile = self.config['logfile']

            if self.logging:
                self.log = open(self.logfile, 'wb')

        # just Windows things...
        if os.name == 'nt':
            try:
                tmp_ssh = paramiko.SSHClient()
                tmp_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self._ssh.connect(ip, username=username, password=password, timeout=1)
            except:
                # Quietly face the Windows struggle with 1st connection
                pass

        # SSH connection
        try:
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._ssh.connect(ip, username=username, password=password)
        except (paramiko.ssh_exception.NoValidConnectionsError, TimeoutError):
            print(f"\tWARNING: Could not connect to the host {self.ip} - will be skipped")
            self._ssh = None
            self.status_ok = False

    def log_input(self, command):
        line_to_log = f"IN {self.ip} << {command}\n"
        if self.verbose:
            print(line_to_log)
        if self.logging:
            self.log.write(line_to_log.encode('utf-8', 'replace'))

    def log_output(self, command):
        log_command = f"OUT {self.ip} >> {command}\n"
        if self.verbose:
            print(log_command)
        if self.logging:
            self.log.write(log_command.encode('utf-8', 'replace'))

    def get_connection_successful(self):
        return self.status_ok

    def sudo_command(self, command, bypass_sudo_password=False):
        self.log_output(command)

        stdin, stdout, stderr = self._ssh.exec_command(f"sudo {command}", get_pty=True)
        # Small delay for password prompt to appear:
        time.sleep(1)
        if not bypass_sudo_password:
            stdin.write(f"{self.password}\n")
            stdin.flush()

        # Blocking and waiting for command output so we know it has completed.
        result = stdout.readlines()

        for line in result:
            self.log_input(line)

        return result

    def command(self, command):
        self.log_output(command)

        streams = self._ssh.exec_command(command)

        for line in streams[1].readlines():
            self.log_input(line)

        return streams

    def reconnect(self, delay):
        # close the connection and give rpi some time for reboot. Then restore connection.
        self._ssh.close()
        time.sleep(delay)
        self._ssh.connect(self.ip, username=self.username, password=self.password)
        print("Reconnected")

    def __del__(self):
        if self.logging:
            self.log.close()
        if self._ssh is None:
            return
        print(f"Closing connection to remote {self.ip}")
        self._ssh.close()
