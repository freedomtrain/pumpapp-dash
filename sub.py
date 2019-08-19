import paho.mqtt.client as mqtt
import time
import sqlite3



#def on_connect(client, userdata, flags, rc):
   #print("Connected With Result Code "+rc)

def on_message_flow(client, userdata, msg):
	global flow 
	flow = float(msg.payload.decode())
	return flow

def on_message_flow2(client, userdata, msg):
	global flow2
	flow2 = float(msg.payload.decode())
	return flow2

def on_message_pressure(client, userdata, msg):
	global pressure 
	pressure = float(msg.payload.decode())
	return pressure

def on_message_power(client, userdata, msg):
	global power 
	power = float(msg.payload.decode())
	return power

def on_message_pressure2(client, userdata, msg):
	global pressure2
	pressure2 = float(msg.payload.decode())
	return pressure2


#def on_subscribe(mosq, obj, mid, granted_qos):
    #print("Subscribe request acknowledged.")
#    return

client = mqtt.Client()
client.username_pw_set("yxlhuqjo", "MMLsMSP-IUSv")
client.connect('postman.cloudmqtt.com', 13872, 60)
#client.on_connect = on_connect
#client.on_subscribe = on_subscribe
client.message_callback_add("/cloudmqtt/flow", on_message_flow)
client.message_callback_add("/cloudmqtt/flow2", on_message_flow2)
client.message_callback_add("/cloudmqtt/pressure", on_message_pressure)
client.message_callback_add("/cloudmqtt/power", on_message_power)
client.message_callback_add("/cloudmqtt/pressure2", on_message_pressure2)
sq = sqlite3.connect(database="db.sqlite3")

flow = 1.00420691
flow2 = 1.00420691
power = 1.00420691
pressure = 1.00420691
pressure2 = 1.00420691

#Motor Pump
efficiencyMotor = 96
#Piping & hydraulics
staticSuction = 3 
staticDischarge = 52
#other parameters
priceElectric = 0.139
emission = 0.538
density = 1000
gravity = 9.81
operating = 16

client.loop_start()
run = True
while run:
	client.subscribe("/cloudmqtt/flow", 1)
	client.subscribe("/cloudmqtt/flow2", 1)
	client.subscribe("/cloudmqtt/pressure", 1)
	client.subscribe("/cloudmqtt/power",1)
	client.subscribe("/cloudmqtt/pressure2", 1)

	powerMotorshaft = (efficiencyMotor/100)*power
	totalHead = staticSuction + pressure
	powerHydraulic = (flow*density*gravity*totalHead)/3670000
	frictionlosses = pressure - staticDischarge
	efficiencyHydraulic = 100*(powerHydraulic/powerMotorshaft)
	efficiencyPiping = 100*(1-(frictionlosses/pressure))
	efficiencyOverall = efficiencyMotor*efficiencyHydraulic*efficiencyPiping/(10000)
	consumptionElectric = power*operating
	costElectric = consumptionElectric*priceElectric
	displacedFluids = flow*operating
	emittedCO2 = emission*consumptionElectric

	c = sq.cursor()
	if flow == 1.00420691 or flow2 == 1.00420691 or power == 1.00420691 or pressure == 1.00420691 or pressure2 == 1.00420691:
		print("Subscribing to CloudMQTT... ")
	else:
		c.execute ("insert into myapp_pump (flow, flow2, pressure, pressure2, power, efficiencyHydraulic, efficiencyPiping, efficiencyOverall, consumptionElectric, costElectric, displacedFluids, emittedCO2, pump_time) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'));", (flow, flow2, pressure, pressure2, power, efficiencyHydraulic, efficiencyPiping, efficiencyOverall, consumptionElectric, costElectric, displacedFluids, emittedCO2))
		sq.commit()
		c.execute ( "select * from myapp_pump order by pump_time desc;")
		yey = c.fetchone()
		print (yey)
	time.sleep(15)

	

