####################################
#	temperature_v_time.py 		 	   
#	Python 3.x 				
#	Kurt Manrique-Nino	   
####################################

import os
import numpy as np
import matplotlib.pyplot as plt
import sys
from datetime import datetime

def get_delta_time(time1, time2):
	delta_t = time2 - time1
	return delta_t.total_seconds()

def parse_time_par_file(path):
	str_time_arr = []
	time_arr = []
	delta_time_arr = []
	with open(path) as par_file:
		for line in par_file:			
			str_time_arr.append(line[4:24])
	str_time_arr.pop(0)
	for time in str_time_arr:
		time_arr.append(datetime.strptime(time, "%b %d %H:%M:%S %Y"))
	for time in time_arr:
		delta_time_arr.append(get_delta_time(time_arr[0], time))
	return delta_time_arr		

def parse_temperature_par_file(path):
	temperature_arr = np.genfromtxt(path, delimiter = ' ', usecols = -2)
	return temperature_arr

def parse_first_scan_par_file(path):
	scan = 0
	with open(path) as par_file:
		counter = 0
		for line in par_file:
			counter += 1
			if(counter == 2):
				temp = line.split()
				scan = int(temp[7])
	return scan

def get_subdirs(root):
	for src, dirs, files in os.walk(root):
		return dirs

def build_chi_paths(subdirs, root, start_from_scan):
	sort_subdirs = list(map(int, results))
	sort_subdirs.sort()
	root_dir = root
	paths = []
	full_paths = []
	if(root_dir[len(root) - 1] != '/'):
		root_dir += '/'
	else:
		pass
	for sub in range(0, len(sort_subdirs) + 1):
		paths.append('%s%d%s'%(root_dir, sub, '/'))
	trimmed_paths = paths[start_from_scan:]
	for path in trimmed_paths:
		for src, dirs, files in os.walk(path):
			for file in files:
				if(file.endswith('.chi')):
					temp = os.path.join(src, file)
					full_paths.append(temp)
	return full_paths
		
def parse_angle_chi_files(arrayPaths):
	angle_arr = np.genfromtxt(arrayPaths[0], delimiter = ' ', usecols = 0)
	return angle_arr

def parse_intensity_chi_files(arrayPaths):
	collection_intensity = []
	for path in arrayPaths:
		intensity_arr = []
		intensity = np.genfromtxt(path, delimiter = ' ', usecols = 1)
		for i in range(0, intensity.size):
			collection_intensity.append(intensity[i])
	return collection_intensity

def display_graphs(angle_arr, time_arr, intensity_arr, temperature_arr, path, zi, zf):
	#controur graph data
	x = np.array(angle_arr)
	y = np.array(time_arr)
	x1, y1 = np.meshgrid(x, y)
	z = np.array(intensity_arr).reshape(x1.shape)
	#subplots
	f, (g1, g2, g3) = plt.subplots(1, 3)
	fileName = path.split('/')
	f.suptitle(fileName[len(fileName) - 2])
	#subplot plot
	g1.plot(temperature_arr, time_arr, 'b')
	g1.set_xlabel('Temperture')
	g1.set_ylabel('Time (seconds)')
	g1.set_ylim([y[0], y[len(y) - 1]])
	g1.grid()
	#subplot contour
	g2.contourf(x1, y1, z)
	g2.set_xlabel('Angle (degrees)')
	g2.set_ylabel('Time (seconds)')
	#subplot zoom-in
	if(zi < angle_arr[0] or zi > zf or zf > angle_arr[len(angle_arr) - 1]):
		print('Invalid values to generate zoomed contour graph')
	else: 
		g3.contourf(x1, y1, z)
		g3.set_xlim([zi, zf])
		g3.set_xlabel('Angle (degrees)')
		g3.set_ylabel('Time (seconds)')
	plt.show()

root_directory = input('Enter the path to the root folder path: ')
par_file_path = input('Enter the path to the raw .par file: ')
print('-----Zoom contour graph by angle (degrees)-----')
zoom_contour_from = float(input('From: '))
zoom_contour_to = float(input('To: '))

time_array = parse_time_par_file(par_file_path)
temperature_array = parse_temperature_par_file(par_file_path)
start_from_scan = parse_first_scan_par_file(par_file_path)
raw_subdirs = get_subdirs(root_directory)
chi_paths = build_chi_paths(raw_subdirs, root_directory, start_from_scan)
angle_array = parse_angle_chi_files(chi_paths)
intensity_array = parse_intensity_chi_files(chi_paths)
display_graphs(angle_array, time_array, intensity_array, temperature_array, par_file_path, zoom_contour_from, zoom_contour_to)