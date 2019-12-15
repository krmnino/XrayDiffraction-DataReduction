####################################
#	potential_v_time.py 			
#	Python 3.x						
#	Kurt Manrique-Nino
####################################

import os
import numpy as np
import matplotlib.pyplot as plt
import sys
from datetime import datetime

def acquisition_time(path):
	acq_time = None
	with open(path) as data:
		counter = 0
		for line in data:
			counter += 1
			if(counter == 14):
				acq_time = datetime.strptime(((line[25:len(line) - 1])), "%m/%d/%Y %H:%M:%S")
				break
	return acq_time

def range_mpt_file(path):
	with open(path) as mpt:
		mpt_start = 0
		for line, x in enumerate(mpt):
			if(line == 1):
				splitLine = x.split()
				mpt_start += int(splitLine[len(splitLine)-1])
				break
	return mpt_start

def getDeltaTime(time1, time2):
	delta_t = time2 - time1
	return delta_t.total_seconds()

def raw_spec_times(path, acq_time, trim):
	scan_time = []
	delta_times = []
	with open(path) as spec_log:
		skip = False
		for i in spec_log:
			for j in i.split():
				if(j == '#D'):
					scan_time.append(datetime.strptime(i[7:len(i)-1], "%b %d %H:%M:%S %Y"))
	for scan in range(0, len(scan_time)):
			delta_times.append(getDeltaTime(acq_time, scan_time[scan]))
	trimmed_delta_times = delta_times[trim:]
	return trimmed_delta_times

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
	subdirs.sort()
	root_dir = root
	paths = []
	full_paths = []
	if(root_dir[len(root) - 1] != '/'):
		root_dir += '/'
	else:
		pass
	for sub in range(0, len(subdirs) + 1):
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

def display_graphs(angle_arr, time_arr, intensity_arr, path, theRange, zi, zf):
	#plot graph data
	time = np.genfromtxt(path, delimiter = '\t', skip_header = theRange, usecols = 7)
	potential = np.genfromtxt(path, delimiter = '\t', skip_header = theRange, usecols = 11)
	#controur graph data
	x = np.array(angle_arr)
	y = np.array(time_arr)
	x1, y1 = np.meshgrid(x, y)
	z = np.array(intensity_arr).reshape(x1.shape)
	#subplots
	f, (g1, g2, g3) = plt.subplots(1, 3)
	fileName = path.split('/')
	f.suptitle(fileName[len(fileName) - 1])
	#subplot plot
	g1.plot(potential, time, 'b')
	g1.set_xlabel('Ewe/V')
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
spec_log_path = input('Enter the path to the SPEC log file: ')
par_file_path = input('Enter the path to the .par file: ')
mpt_file_path = input('Enter the path to the .mpt file: ')
print('-----Zoom contour graph by angle (degrees)-----')
zoom_contour_from = int(input('From: '))
zoom_contour_to = int(input('To: '))

start_from_scan = parse_first_scan_par_file(par_file_path)
raw_subdirs = get_subdirs(root_directory)
chi_paths = build_chi_paths(raw_subdirs, root_directory, start_from_scan)
acq_time = acquisition_time(mpt_file_path)
angle_array = parse_angle_chi_files(chi_paths)
intensity_array = parse_intensity_chi_files(chi_paths)
time_array = raw_spec_times(spec_log_path, acq_time, start_from_scan)
range_mpt = range_mpt_file(mpt_file_path)
display_graphs(angle_array, time_array, intensity_array, mpt_file_path, range_mpt, zoom_contour_from, zoom_contour_to)