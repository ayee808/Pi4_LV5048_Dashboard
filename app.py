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


@app.route('/stats')
def stats():
	# timestamp
	now = datetime.now()
	time = now.strftime("%m/%d/%Y - %H:%M:%S")

	# connect to database
	conn = sqlite3.connect('/home/pi/Documents/Solar.db')
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	# Get all data for the current year in one query
	cur.execute("select timestamp,battery_voltage,battery_charging_current,battery_discharge_current from LV5048 where strftime('%Y', timestamp) = strftime('%Y', 'now','localtime') order by timestamp")
	year_data = cur.fetchall()

	# Group data by date for processing
	daily_data = {}
	for row in year_data:
		timestamp = row[0]
		date_key = dateutil.parser.isoparse(timestamp).date().isoformat()
		if date_key not in daily_data:
			daily_data[date_key] = []
		daily_data[date_key].append(row)

	# Helper function to calculate energy for a set of rows
	def calculate_energy(rows):
		generated = 0.0
		consumed = 0.0
		for i in range(len(rows) - 1):
			current_time = dateutil.parser.isoparse(rows[i][0])
			next_time = dateutil.parser.isoparse(rows[i + 1][0])
			time_delta_hours = (next_time - current_time).total_seconds() / 3600.0

			battery_voltage = rows[i][1] if rows[i][1] else 0.0
			charging_current = rows[i][2] if rows[i][2] else 0.0
			discharge_current = rows[i][3] if rows[i][3] else 0.0

			generated_power_kw = (battery_voltage * charging_current) / 1000.0
			consumed_power_kw = (battery_voltage * discharge_current) / 1000.0

			generated += generated_power_kw * time_delta_hours
			consumed += consumed_power_kw * time_delta_hours

		return generated, consumed

	# Calculate today's totals
	today_date = now.date().isoformat()
	dailyGenerated = 0.0
	dailyConsumed = 0.0
	if today_date in daily_data:
		dailyGenerated, dailyConsumed = calculate_energy(daily_data[today_date])

	# Calculate daily totals for current month
	current_month = now.strftime('%Y-%m')
	monthlyGenerated = []
	monthlyConsumed = []

	for date_key in sorted(daily_data.keys()):
		if date_key.startswith(current_month):
			day_generated, day_consumed = calculate_energy(daily_data[date_key])
			monthlyGenerated.append({"x": date_key, "y": round(day_generated, 2)})
			monthlyConsumed.append({"x": date_key, "y": round(day_consumed, 2)})

	# Calculate monthly totals for current year
	monthly_totals = {}
	for date_key in daily_data.keys():
		month_key = date_key[:7]  # YYYY-MM format
		if month_key not in monthly_totals:
			monthly_totals[month_key] = {'generated': 0.0, 'consumed': 0.0}

		day_generated, day_consumed = calculate_energy(daily_data[date_key])
		monthly_totals[month_key]['generated'] += day_generated
		monthly_totals[month_key]['consumed'] += day_consumed

	yearlyGenerated = []
	yearlyConsumed = []
	for month_key in sorted(monthly_totals.keys()):
		yearlyGenerated.append({"x": month_key + "-01", "y": round(monthly_totals[month_key]['generated'], 2)})
		yearlyConsumed.append({"x": month_key + "-01", "y": round(monthly_totals[month_key]['consumed'], 2)})

	conn.close()

	return render_template('stats.html',
						 time=time,
						 dailyGenerated=round(dailyGenerated, 2),
						 dailyConsumed=round(dailyConsumed, 2),
						 monthlyGenerated=monthlyGenerated,
						 monthlyConsumed=monthlyConsumed,
						 yearlyGenerated=yearlyGenerated,
						 yearlyConsumed=yearlyConsumed)

if __name__ == '__main__':
	app.run(debug = True, host='0.0.0.0')
