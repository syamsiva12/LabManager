import sys
import re
sys.path.append(r'D:/backup/PRO/')
from  lib.initiate_ssh_connection import SSHClient
import mysql.connector
import socket
import json
import threading
import time
import requests
import os
import logging

# Setting logger 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Interface to be igonred
ignore_interface = ['cni-podman0', 'fptun0',  'lo',  'veth', 'vneth', 'vnet','io','cni-podman0', 'eth-int', 'vethb', 'vnet', 'vnet','cni-podman1','docker0']

# Setting SQL Connect 
def sql_connect():
    host = "192.168.109.137"
    port = 3306
    user = "root"
    password = "password"
    database = "DEVICE_TRACKER"

    # Establish a connection to the database
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    return connection
# Function for retreving data from mysql database
def get_dev_details():
    dev = {}
    connection = sql_connect()
    try:
    # Create a cursor to execute SQL queries
        cursor = connection.cursor()

        # Define the SQL query to retrieve IP and TAG from DEVICES table
        query = r"SELECT ip, tags, ip2, ip3 FROM field"

        # Execute the query
        cursor.execute(query)

        # Fetch all the rows
        rows = cursor.fetchall()

        # Print the results
        for row in rows:
            ip, tag, ip2, ip3 = row
            dev[tag] = {ip, ip2, ip3}

    except:
        logger.critical("Failed to featch database")
        os.environ['state'] = 'IDLE'
        logger.info("Released Trigger Lock")
  #  cursor.close()
    connection.close()
    return dev
# Function for retriving username and password of spcific device
def get_pass_details(ip):
    connection = sql_connect()
    cursor = connection.cursor()
    query =  r"SELECT username, password FROM field WHERE ip = %s OR ip2 = %s OR ip3 = %s"
    cursor.execute(query, (ip,ip,ip))
    cred = cursor.fetchone()
    connection.close()
    return cred

# Function for getting ping status
def check_ping(devices):
    status_info = {}
    ssh_list  = []
    for tag, msip in devices.items():
        ping_status = {}
        for ip in msip:
            try:
            # Create a socket object and attempt to connect to the IP address on port 80
                sock = socket.create_connection((ip, 22), timeout=2)
                sock.close()
                ping_status[ip] = 'UP'
            except(socket.timeout, socket.error):
                ping_status[ip] = 'DOWN'
        status_info[tag] = ping_status
    for tag,dev_list in status_info.items():
        for ip,status in dev_list.items():
            if status=='UP':
                ssh_list.append(ip)
                break
    return status_info, ssh_list

# Removing unwante interface
def procees_interface(inf):
    final_inf = []
    try:
        inf.remove('')
    except ValueError:
        pass

    for i in inf:
        if i[-1] == ':':
            final_inf.append(i[:-1])
        else:
            final_inf.append(i)

    final_inf = [interface for interface in final_inf if not any(ignore in interface for ignore in ignore_interface)]

    return final_inf

# Get tag based on the interface
def get_tag(ip):
    sql_query = "SELECT tags FROM field WHERE ip = %s OR ip2 = %s OR ip3 = %s;"
    connection = sql_connect()  # Make sure to implement your sql_connect function
    cursor = connection.cursor()
    cursor.execute(sql_query, (ip, ip, ip))
    tags = cursor.fetchall()
    return tags
    
# Function of interface status
def initiate_ssh(l):
    status_check = {}
    layer_status = {}
    for ip in l:
            ifconfig_status = ''
            route_status = ''
            arp_status = ''
            status = {}
            l_status = {}
            username, password = get_pass_details(ip)
            obj = SSHClient(ip,username,password)
            obj.connect()
            try:
                interface = str(obj.run_execmcd("ifconfig  | awk '/^[a-zA-Z]/{print $1}'"))
                interface = interface.split('\n')        
                interface = procees_interface(interface)
                ifconfig_status = obj.run_execmcd('ifconfig')
                route_status = obj.run_execmcd('route -n')
                arp_status = obj.run_execmcd('arp -a')
                for i in interface:
                    link = obj.run_execmcd(f"ethtool {i} | grep 'Link detected' | awk '{{print $3}}'")
                    if(link.strip() == 'yes'):
                        status[i] = 'UP'
                    else:
                        status[i] = 'DOWN'
                tag = get_tag(ip)
                tag = tag[0][0]
                status_check[tag] = status
                l_status['ifconfig'] = ifconfig_status
                l_status['route'] = route_status
                l_status['arp'] = arp_status
                layer_status[tag] = l_status
                obj.close_connection()
            except:
                logger.critical("Issue facing while running ethtool") # Failed to SSH
    return json.dumps(status_check), json.dumps(layer_status)
