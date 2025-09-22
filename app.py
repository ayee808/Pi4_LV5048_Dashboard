from flask import Flask, render_template, request, jsonify
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

@app.route('/sys_status')
def sys_status():
	
	# timestamp	
	now = datetime.now()
	time = now.strftime("%m/%d/%Y - %H:%M:%S")
	timeStamp = now.isoformat()
	# get the data from the inverter
	try:
		statusMsg = os.popen("sudo mpp-solar -c QPIGS -d /dev/hidraw0").read()
	except:
		return render_template('system_status.html', activePower = 0,
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
		
		return render_template('system_status.html', activePower = statusVals.get("ac_output_active_power"),
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
		return render_template('system_status.html', activePower = 0,
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

def get_chart_data(period='last36hours'):
	# connect to database
	conn = sqlite3.connect('/home/pi/Documents/Solar.db')
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	# Determine time filter based on period
	if period == 'last36hours':
		time_filter = "datetime(timestamp) > datetime('now','-36 hours','localtime')"
	elif period == 'last7days':
		time_filter = "datetime(timestamp) > datetime('now','-7 days','localtime')"
	elif period == 'last30days':
		time_filter = "datetime(timestamp) > datetime('now','-30 days','localtime')"
	else:
		time_filter = "datetime(timestamp) > datetime('now','-36 hours','localtime')"  # default to last 36 hours

	cur.execute(f"select timestamp,pv_input_power,ac_output_active_power,battery_charging_current,battery_discharge_current,battery_voltage,inverter_heat_sink_temperature,rasberryPi_temperature from LV5048 where {time_filter} order by timestamp")
	rows = cur.fetchall()

	# Chart 1 calculated power data (using same methodology as stats endpoint)
	calcGeneration = []
	calcUsage = []

	# Calculate total energy using same integration method as stats endpoint
	totalGenerated = 0.0
	totalConsumed = 0.0

	for i in range(len(rows) - 1):
		current_time = dateutil.parser.isoparse(rows[i][0])
		next_time = dateutil.parser.isoparse(rows[i + 1][0])
		time_delta_hours = (next_time - current_time).total_seconds() / 3600.0

		battery_voltage = rows[i][5] if rows[i][5] else 0.0
		charge_current = rows[i][3] if rows[i][3] else 0.0
		discharge_current = rows[i][4] if rows[i][4] else 0.0

		# Use same calculation as stats: voltage × current
		generated_power = battery_voltage * charge_current
		consumed_power = battery_voltage * discharge_current

		# Add to chart data
		calcGeneration.append({"x" : rows[i][0], "y" : generated_power})
		calcUsage.append({"x" : rows[i][0], "y" : consumed_power})

		# Calculate energy totals (power × time)
		generated_power_kw = generated_power / 1000.0
		consumed_power_kw = consumed_power / 1000.0

		totalGenerated += generated_power_kw * time_delta_hours
		totalConsumed += consumed_power_kw * time_delta_hours

	# Add the last data point for chart display
	if rows:
		last_row = rows[-1]
		battery_voltage = last_row[5] if last_row[5] else 0.0
		charge_current = last_row[3] if last_row[3] else 0.0
		discharge_current = last_row[4] if last_row[4] else 0.0

		generated_power = battery_voltage * charge_current
		consumed_power = battery_voltage * discharge_current

		calcGeneration.append({"x" : last_row[0], "y" : generated_power})
		calcUsage.append({"x" : last_row[0], "y" : consumed_power})

	# Chart 2 power data (PV Array 1 only)
	pvwatts = []
	for row in rows:
		pvwatts.append({"x" : row[0], "y" : row[1]})
	usedwatts = []
	for row in rows:
		usedwatts.append({"x" : row[0], "y" : row[2]})
	# Chart 3 batt data
	volts = []
	for row in rows:
		volts.append({"x" : row[0], "y" : row[5]})
	chargeAmps = []
	for row in rows:
		chargeAmps.append({"x" : row[0], "y" : row[3]})
	dischargeAmps = []
	for row in rows:
		dischargeAmps.append({"x" : row[0], "y" : row[4]})
	# Chart 4 temps
	inverterTemps = []
	for row in rows:
		inverterTemps.append({"x" : row[0], "y" : row[6]})
	piTemps = []
	for row in rows:
		piTemps.append({"x" : row[0], "y" : row[7]})

	conn.close()

	return {
		'calcGeneration': calcGeneration,
		'calcUsage': calcUsage,
		'pvwatts': pvwatts,
		'usedwatts': usedwatts,
		'volts': volts,
		'chargeAmps': chargeAmps,
		'dischargeAmps': dischargeAmps,
		'inverterTemps': inverterTemps,
		'piTemps': piTemps,
		'totalGenerated': round(totalGenerated, 2),
		'totalConsumed': round(totalConsumed, 2)
	}

@app.route('/data_endpoint')
def data_endpoint():
	period = request.args.get('period', 'today')
	data = get_chart_data(period)
	return jsonify(data)

@app.route('/data')
def data():
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
	
	# Get chart data using helper function (default to last 36 hours)
	chart_data = get_chart_data('last36hours')

	return render_template('data.html',
						 time=time,
						 calcGeneration=chart_data['calcGeneration'],
						 calcUsage=chart_data['calcUsage'],
						 pvwatts=chart_data['pvwatts'],
						 usedwatts=chart_data['usedwatts'],
						 volts=chart_data['volts'],
						 chargeAmps=chart_data['chargeAmps'],
						 dischargeAmps=chart_data['dischargeAmps'],
						 inverterTemps=chart_data['inverterTemps'],
						 piTemps=chart_data['piTemps'])

	





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
		gen_total = round(monthly_totals[month_key]['generated'], 2)
		con_total = round(monthly_totals[month_key]['consumed'], 2)
		yearlyGenerated.append({"x": month_key + "-01", "y": gen_total})
		yearlyConsumed.append({"x": month_key + "-01", "y": con_total})

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
