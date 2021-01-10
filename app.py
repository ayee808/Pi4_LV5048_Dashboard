from flask import Flask, render_template
import os
import re
from datetime import datetime
import dateutil.parser
import sqlite3
import json

app = Flask(__name__)

maxLoad = 5000
minVoltage = 48
maxVoltage = 58
maxChargeCurrent = 20
maxDischargeCurrent = 120
maxInverterTemp = 60
maxInputCurrent = 20
maxInputVoltage = 105
maxInputPower = 1300
maxPiTemp = 85

@app.route('/dashboard')
def dashboard():
	
	# timestamp	
	now = datetime.now()
	time = now.strftime("%m/%d/%Y - %H:%M:%S")
	timeStamp = now.isoformat()
	# get the data from the inverter
	try:
		statusMsg = os.popen("sudo mpp-solar -c QPIGS -d /dev/hidraw0").read()
	except:
		return render_template('dashboard.html', activePower = 0,
											 outputLoad = 0,
											 batteryChargeCurrent = 0,
											 batteryDischargeCurrent = 0,
											 batteryVoltage = 0,
											 inverterTemp = 0,
											 isCharging = "",
											 isChargingToFloat = "",
											 pvInputCurrent = 0,
											 pvInputPower = 0,
											 pvInputVoltage = 0,
											 piTemp = 0,
											 time = time,
											 activePowerPct = 0,
											 batteryChargeCurrentPct = 0,
											 batteryDischargeCurrentPct = 0,
											 batteryVoltagePct = 0,
											 inverterTempPct = 0,
											 pvInputCurrentPct = 0,
											 pvInputPowerPct = 0,
											 pvInputVoltagePct = 0,
											 piTempPct = 0)
	statusArr = re.split(r'\s\s+|\t|\n',statusMsg)
	# reformat status message raw
	# statusMsg = statusMsg.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")#.replace("\n","<br>")
	# print(statusMsg)
	
	# start a dictionary to store data
	statusVals = dict()
	
	# get rasberry pi temperature
	piTemp = float(os.popen("/opt/vc/bin/vcgencmd measure_temp").read().replace("temp=","").replace("\'C\n",""))
	
	statusVals["piTemp"] = piTemp
	validData = False
	for idx,chunk in enumerate(statusArr, start=0):
		if chunk == "ac_output_active_power":
			statusVals[chunk] = int(statusArr[idx + 1])
		elif chunk == "ac_output_load":
			statusVals[chunk] = int(statusArr[idx + 1])
		elif chunk == "battery_charging_current":
			statusVals[chunk] = int(statusArr[idx + 1])
		elif chunk == "battery_discharge_current":
			statusVals[chunk] = int(statusArr[idx + 1])
		elif chunk == "battery_voltage":
			statusVals[chunk] = float(statusArr[idx + 1])
			validData = True
		elif chunk == "inverter_heat_sink_temperature":
			statusVals[chunk] = int(statusArr[idx + 1])
		elif chunk == "is_charging_on":
			statusVals[chunk] = bool(statusArr[idx + 1])
		elif chunk == "is_charging_to_float":
			statusVals[chunk] = bool(statusArr[idx + 1])
		elif chunk == "pv_input_current_for_battery":
			statusVals[chunk] = float(statusArr[idx + 1])
		elif chunk == "pv_input_power":
			statusVals[chunk] = int(statusArr[idx + 1])
		elif chunk == "pv_input_voltage":
			statusVals[chunk] = float(statusArr[idx + 1])
	
	# connect to database
	conn = sqlite3.connect('/home/pi/Documents/Solar.db')
	if (validData):
		conn.execute("INSERT INTO LV5048 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", [timeStamp,
																		  piTemp,
																		  statusVals.get("ac_output_active_power"),
																		  statusVals.get("ac_output_load"),
																		  statusVals.get("battery_charging_current"),
																		  statusVals.get("battery_discharge_current"),
																		  statusVals.get("battery_voltage"),
																		  statusVals.get("inverter_heat_sink_temperature"),
																		  statusVals.get("is_charging_on"),
																		  statusVals.get("is_charging_to_float"),
																		  statusVals.get("pv_input_current_for_battery"),
																		  statusVals.get("pv_input_power"),
																		  statusVals.get("pv_input_voltage")])
		conn.commit()
		
		return render_template('dashboard.html', activePower = statusVals.get("ac_output_active_power"),
											 outputLoad = statusVals.get("ac_output_load"),
											 batteryChargeCurrent = statusVals.get("battery_charging_current"),
											 batteryDischargeCurrent = statusVals.get("battery_discharge_current"),
											 batteryVoltage = statusVals.get("battery_voltage"),
											 inverterTemp = statusVals.get("inverter_heat_sink_temperature"),
											 isCharging = "checked" if statusVals.get("is_charging_on") == True else "",
											 isChargingToFloat = "checked" if statusVals.get("is_charging_to_float") == True else "",
											 pvInputCurrent = statusVals.get("pv_input_current_for_battery"),
											 pvInputPower = statusVals.get("pv_input_power"),
											 pvInputVoltage = statusVals.get("pv_input_voltage"),
											 piTemp = statusVals.get("piTemp"),
											 time = time,
											 activePowerPct = int(statusVals.get("ac_output_active_power") * 100 / maxLoad),
											 batteryChargeCurrentPct = int(statusVals.get("battery_charging_current") * 100 / maxChargeCurrent),
											 batteryDischargeCurrentPct = int(statusVals.get("battery_discharge_current") * 100 / maxDischargeCurrent),
											 batteryVoltagePct = (int(statusVals.get("battery_voltage") - minVoltage) * 100 / (maxVoltage - minVoltage)),
											 inverterTempPct = int(statusVals.get("inverter_heat_sink_temperature") * 100 / maxInverterTemp),
											 pvInputCurrentPct = int(statusVals.get("pv_input_current_for_battery") * 100 / maxInputCurrent),
											 pvInputPowerPct = int(statusVals.get("pv_input_power") * 100 / maxInputPower),
											 pvInputVoltagePct = int(statusVals.get("pv_input_voltage") * 100 / maxInputVoltage),
											 piTempPct = int(statusVals.get("piTemp") * 100 / maxPiTemp))
	else:
		return render_template('dashboard.html', activePower = 0,
											 outputLoad = 0,
											 batteryChargeCurrent = 0,
											 batteryDischargeCurrent = 0,
											 batteryVoltage = 0,
											 inverterTemp = 0,
											 isCharging = "",
											 isChargingToFloat = "",
											 pvInputCurrent = 0,
											 pvInputPower = 0,
											 pvInputVoltage = 0,
											 piTemp = 0,
											 time = time,
											 activePowerPct = 0,
											 batteryChargeCurrentPct = 0,
											 batteryDischargeCurrentPct = 0,
											 batteryVoltagePct = 0,
											 inverterTempPct = 0,
											 pvInputCurrentPct = 0,
											 pvInputPowerPct = 0,
											 pvInputVoltagePct = 0,
											 piTempPct = 0)
		

	conn.close()
	
@app.route('/day')
def day():
	# timestamp	
	now = datetime.now()
	time = now.strftime("%m/%d/%Y - %H:%M:%S")
	timeStamp = now.isoformat()
	
	# get the data from the inverter
	try:
		statusMsg = os.popen("sudo mpp-solar -c QPIGS -d /dev/hidraw0").read()
		statusArr = re.split(r'\s\s+|\t|\n',statusMsg)
		# reformat status message raw
		# statusMsg = statusMsg.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")#.replace("\n","<br>")
		# print(statusMsg)
		
		# start a dictionary to store data
		statusVals = dict()
		
		# get rasberry pi temperature
		piTemp = float(os.popen("/opt/vc/bin/vcgencmd measure_temp").read().replace("temp=","").replace("\'C\n",""))
		
		statusVals["piTemp"] = piTemp
		validData = False
		for idx,chunk in enumerate(statusArr, start=0):
			if chunk == "ac_output_active_power":
				statusVals[chunk] = int(statusArr[idx + 1])
			elif chunk == "ac_output_load":
				statusVals[chunk] = int(statusArr[idx + 1])
			elif chunk == "battery_charging_current":
				statusVals[chunk] = int(statusArr[idx + 1])
			elif chunk == "battery_discharge_current":
				statusVals[chunk] = int(statusArr[idx + 1])
			elif chunk == "battery_voltage":
				statusVals[chunk] = float(statusArr[idx + 1])
				validData = True
			elif chunk == "inverter_heat_sink_temperature":
				statusVals[chunk] = int(statusArr[idx + 1])
			elif chunk == "is_charging_on":
				statusVals[chunk] = bool(statusArr[idx + 1])
			elif chunk == "is_charging_to_float":
				statusVals[chunk] = bool(statusArr[idx + 1])
			elif chunk == "pv_input_current_for_battery":
				statusVals[chunk] = float(statusArr[idx + 1])
			elif chunk == "pv_input_power":
				statusVals[chunk] = int(statusArr[idx + 1])
			elif chunk == "pv_input_voltage":
				statusVals[chunk] = float(statusArr[idx + 1])
		
		if (validData):
			# connect to database
			conn = sqlite3.connect('/home/pi/Documents/Solar.db')
			conn.execute("INSERT INTO LV5048 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", [timeStamp,
																			  piTemp,
																			  statusVals.get("ac_output_active_power"),
																			  statusVals.get("ac_output_load"),
																			  statusVals.get("battery_charging_current"),
																			  statusVals.get("battery_discharge_current"),
																			  statusVals.get("battery_voltage"),
																			  statusVals.get("inverter_heat_sink_temperature"),
																			  statusVals.get("is_charging_on"),
																			  statusVals.get("is_charging_to_float"),
																			  statusVals.get("pv_input_current_for_battery"),
																			  statusVals.get("pv_input_power"),
																			  statusVals.get("pv_input_voltage")])
			conn.commit()
	except:
		print("Inverter query failed")
	
	# connect to database
	conn = sqlite3.connect('/home/pi/Documents/Solar.db')
	conn.row_factory = sqlite3.Row
   
	cur = conn.cursor()
	cur.execute("select timestamp,pv_input_power,ac_output_active_power,battery_charging_current,battery_discharge_current,battery_voltage,inverter_heat_sink_temperature,rasberryPi_temperature from LV5048 where datetime(timestamp) > datetime('now','-36 hours','localtime')")
	
	rows = cur.fetchall(); 
	#data = [{"x": dateutil.parser.isoparse(row[0]).strftime('%Y-%M-%d HH:mm'), "y": row[1]} for row in rows]
	#return render_template('weekly.html', data = json.dumps(data,ensure_ascii=True))
	
	# Chart 1 power data
	pvwatts = []
	for row in rows:
		pvwatts.append({"x" : row[0], "y" : row[1]})
	usedwatts = []
	for row in rows:
		usedwatts.append({"x" : row[0], "y" : row[2]})
	# Chart 2 batt data
	volts = []
	for row in rows:
		volts.append({"x" : row[0], "y" : row[5]})
	chargeAmps = []
	for row in rows:
		chargeAmps.append({"x" : row[0], "y" : row[3]})
	dischargeAmps = []
	for row in rows:
		dischargeAmps.append({"x" : row[0], "y" : row[4]})
	# Chart 3 temps
	inverterTemps = []
	for row in rows:
		inverterTemps.append({"x" : row[0], "y" : row[6]})
	piTemps = []
	for row in rows:
		piTemps.append({"x" : row[0], "y" : row[7]})
		
	return render_template('day.html', pvwatts = pvwatts, usedwatts = usedwatts, volts = volts, chargeAmps = chargeAmps, dischargeAmps = dischargeAmps, inverterTemps = inverterTemps, piTemps = piTemps)

	

@app.route('/week')
def week():
	# connect to database
	conn = sqlite3.connect('/home/pi/Documents/Solar.db')
	conn.row_factory = sqlite3.Row
   
	cur = conn.cursor()
	cur.execute("select timestamp,pv_input_power,ac_output_active_power,battery_charging_current,battery_discharge_current,battery_voltage,inverter_heat_sink_temperature,rasberryPi_temperature from LV5048 where datetime(timestamp) > datetime('now','-7 day','localtime')")
	
	rows = cur.fetchall(); 
	#data = [{"x": dateutil.parser.isoparse(row[0]).strftime('%Y-%M-%d HH:mm'), "y": row[1]} for row in rows]
	#return render_template('weekly.html', data = json.dumps(data,ensure_ascii=True))
	
	# Chart 1 power data
	pvwatts = []
	for row in rows:
		pvwatts.append({"x" : row[0], "y" : row[1]})
	usedwatts = []
	for row in rows:
		usedwatts.append({"x" : row[0], "y" : row[2]})
	# Chart 2 batt data
	volts = []
	for row in rows:
		volts.append({"x" : row[0], "y" : row[5]})
	chargeAmps = []
	for row in rows:
		chargeAmps.append({"x" : row[0], "y" : row[3]})
	dischargeAmps = []
	for row in rows:
		dischargeAmps.append({"x" : row[0], "y" : row[4]})
	# Chart 3 temps
	inverterTemps = []
	for row in rows:
		inverterTemps.append({"x" : row[0], "y" : row[6]})
	piTemps = []
	for row in rows:
		piTemps.append({"x" : row[0], "y" : row[7]})
		
	return render_template('week.html', pvwatts = pvwatts, usedwatts = usedwatts, volts = volts, chargeAmps = chargeAmps, dischargeAmps = dischargeAmps, inverterTemps = inverterTemps, piTemps = piTemps)

@app.route('/month')
def month():
	# connect to database
	conn = sqlite3.connect('/home/pi/Documents/Solar.db')
	conn.row_factory = sqlite3.Row
   
	cur = conn.cursor()
	cur.execute("select timestamp,pv_input_power,ac_output_active_power,battery_charging_current,battery_discharge_current,battery_voltage,inverter_heat_sink_temperature,rasberryPi_temperature from LV5048 where datetime(timestamp) > datetime('now','-30 day','localtime')")
	
	rows = cur.fetchall(); 
	#data = [{"x": dateutil.parser.isoparse(row[0]).strftime('%Y-%M-%d HH:mm'), "y": row[1]} for row in rows]
	#return render_template('weekly.html', data = json.dumps(data,ensure_ascii=True))
	
	# Chart 1 power data
	pvwatts = []
	for row in rows:
		pvwatts.append({"x" : row[0], "y" : row[1]})
	usedwatts = []
	for row in rows:
		usedwatts.append({"x" : row[0], "y" : row[2]})
	# Chart 2 batt data
	volts = []
	for row in rows:
		volts.append({"x" : row[0], "y" : row[5]})
	chargeAmps = []
	for row in rows:
		chargeAmps.append({"x" : row[0], "y" : row[3]})
	dischargeAmps = []
	for row in rows:
		dischargeAmps.append({"x" : row[0], "y" : row[4]})
	# Chart 3 temps
	inverterTemps = []
	for row in rows:
		inverterTemps.append({"x" : row[0], "y" : row[6]})
	piTemps = []
	for row in rows:
		piTemps.append({"x" : row[0], "y" : row[7]})
		
	return render_template('month.html', pvwatts = pvwatts, usedwatts = usedwatts, volts = volts, chargeAmps = chargeAmps, dischargeAmps = dischargeAmps, inverterTemps = inverterTemps, piTemps = piTemps)
	

@app.route('/year')
def year():
	# connect to database
	conn = sqlite3.connect('/home/pi/Documents/Solar.db')
	conn.row_factory = sqlite3.Row
   
	cur = conn.cursor()
	cur.execute("select timestamp,pv_input_power,ac_output_active_power,battery_charging_current,battery_discharge_current,battery_voltage,inverter_heat_sink_temperature,rasberryPi_temperature from LV5048 where datetime(timestamp) > datetime('now','-365 day','localtime')")
	
	rows = cur.fetchall(); 
	#data = [{"x": dateutil.parser.isoparse(row[0]).strftime('%Y-%M-%d HH:mm'), "y": row[1]} for row in rows]
	#return render_template('weekly.html', data = json.dumps(data,ensure_ascii=True))
	
	# Chart 1 power data
	pvwatts = []
	for row in rows:
		pvwatts.append({"x" : row[0], "y" : row[1]})
	usedwatts = []
	for row in rows:
		usedwatts.append({"x" : row[0], "y" : row[2]})
	# Chart 2 batt data
	volts = []
	for row in rows:
		volts.append({"x" : row[0], "y" : row[5]})
	chargeAmps = []
	for row in rows:
		chargeAmps.append({"x" : row[0], "y" : row[3]})
	dischargeAmps = []
	for row in rows:
		dischargeAmps.append({"x" : row[0], "y" : row[4]})
	# Chart 3 temps
	inverterTemps = []
	for row in rows:
		inverterTemps.append({"x" : row[0], "y" : row[6]})
	piTemps = []
	for row in rows:
		piTemps.append({"x" : row[0], "y" : row[7]})
		
	return render_template('year.html', pvwatts = pvwatts, usedwatts = usedwatts, volts = volts, chargeAmps = chargeAmps, dischargeAmps = dischargeAmps, inverterTemps = inverterTemps, piTemps = piTemps)


if __name__ == '__main__':
	app.run(debug = True, host='0.0.0.0')
