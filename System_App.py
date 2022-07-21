from __future__ import division
import pyrebase
import sys
import json
import os
import paho.mqtt.client as mqtt
import subprocess
import time
import socket


hostname = socket.gethostname()


def check_used_space(path):

    st = os.statvfs(path)

    free_space = st.f_bavail * st.f_frsize

    total_space = st.f_blocks * st.f_frsize

    used_space = int(100 - ((free_space / total_space) * 100))

    return used_space





def check_cpu_load():

    # bash command to get cpu load from uptime command

    p = subprocess.Popen("uptime", shell=True, stdout=subprocess.PIPE).communicate()[0]

    cores = subprocess.Popen("nproc", shell=True, stdout=subprocess.PIPE).communicate()[0]

    cpu_load = str(p).split("average:")[1].split(", ")[0].replace(' ', '').replace(',', '.')

    cpu_load = float(cpu_load) / int(cores) * 100

    cpu_load = round(float(cpu_load), 1)

    return cpu_load





def check_voltage():

    try:

        full_cmd = "vcgencmd measure_volts | cut -f2 -d= | sed 's/000//'"

        voltage = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]

        voltage = voltage.strip()[:-1]

    except Exception:

        voltage = 0

    return voltage





def check_swap():

    full_cmd = "free -t | awk 'NR == 3 {print $3/$2*100}'"

    swap = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]

    swap = round(float(swap.decode("utf-8").replace(",", ".")), 1)

    return swap





def check_memory():

    full_cmd = "free -t | awk 'NR == 2 {print $3/$2*100}'"

    memory = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]

    memory = round(float(memory.decode("utf-8").replace(",", ".")))

    return memory





def check_cpu_temp():

    full_cmd = "cat /sys/class/thermal/thermal_zone*/temp 2> /dev/null | sed 's/\(.\)..$//' | tail -n 1"

    try:

        p = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]

        cpu_temp = p.decode("utf-8").replace('\n', ' ').replace('\r', '')

    except Exception:

        cpu_temp = 0

    return cpu_temp





def check_sys_clock_speed():

    full_cmd = "awk '{printf (\"%0.0f\",$1/1000); }' </sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"

    return subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]





def check_uptime():

    full_cmd = "awk '{print int($1/3600/24)}' /proc/uptime"

    return int(subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0])



def check_model_name():

   full_cmd = "cat /proc/cpuinfo | grep Model | sed 's/Model.*: //g'"

   return subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].decode("utf-8") 



#values = cpu_load, float(cpu_temp), used_space, float(voltage), int(sys_clock_speed), swap, memory, uptime_days

#values = str(values)
config = {
  "apiKey": "AIzaSyBlhkNFcyXOjisSGCb2WB5aQFd7FRf0kBM",
  "authDomain": "ecosystem-4b6c7.firebaseapp.com",
  "databaseURL": "https://ecosystem-4b6c7-default-rtdb.firebaseio.com",
  "storageBucket": "ecosystem-4b6c7.appspot.com",
  "projectId": "ecosystem-4b6c7",
  "storageBucket": "ecosystem-4b6c7.appspot.com",
  "messagingSenderId": "274551526375",
  "appId": "1:274551526375:web:b1e72588275bafcf226342",
  "measurementId": "G-PL3BSE7B0N"
}

firebase = pyrebase.initialize_app(config)
database = firebase.database()
while True:
		cpu_load = check_cpu_load()
		cpu_temp = check_cpu_temp()
		voltage = check_voltage()
		sys_clock_speed = check_sys_clock_speed()
		swap = check_swap()
		memory = check_memory()
		uptime = check_uptime()
		model_name = check_model_name()
		used_space = check_used_space('/')
		#values = cpu_load, float(cpu_temp), used_space, float(voltage), int(sys_clock_speed), swap, memory, uptime
		#values = str(values)[1:-1]
		#data = {"swap": swap,"Uptime": uptime,"model_name": model_name}
		#json.dumps(data)
		data = {"model_name": model_name,"memory": memory,"cpu_temp" : float(cpu_temp),"used_space": float(used_space),"cpu_load": cpu_load,"Voltage": float(voltage)* 3 ,"sys_clock_speed": int(sys_clock_speed)}
		database.push(data)
		
if __name__ == '__main__':

    connect()
