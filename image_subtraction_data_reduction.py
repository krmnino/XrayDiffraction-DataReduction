#########################################
#	image_subtraction_data_reduction.py			
#	Python 3.x						
#	Kurt Manrique-Nino
#########################################

import numpy as np
import os
import gc
import matplotlib.pyplot as plt

import pyFAI
import pyFAI.calibrant
from pyFAI.calibrant import ALL_CALIBRANTS
import fabio
from pyFAI.multi_geometry import MultiGeometry

def get_subdirs(root):
	for src, dirs, files in os.walk(root):
		return dirs

def build_raw_subdirs(subdirs_list, darkfield_file_path, start_from_scan, darkfield_file_within):
	darkfield_file_within = darkfield_file_within.lower()
	darkfield_scan_arr = darkfield_file_path.split('/')
	darkfield_scan_number = int(darkfield_scan_arr[len(darkfield_scan_arr)-3])
	start_from_scan = str(start_from_scan)
	sort_subdirs = []
	if(darkfield_file_within == 'y'):
		for sd in subdirs_list:
			try:
				temp = int(sd)
				if(temp != darkfield_scan_number):
					sort_subdirs.append(temp)
			except:
				pass
	else:
		for sd in subdirs_list:
			try:
				temp = int(sd)
				sort_subdirs.append(temp)
			except:
				pass
	sort_subdirs.sort()
	sort_subdirs = map(str, sort_subdirs)
	for scan in range(0, len(sort_subdirs)):
		if(sort_subdirs[scan] == start_from_scan):
			sort_subdirs = sort_subdirs[scan:]
			break
	return sort_subdirs

def build_scan_file_paths(path, scan_subdirs):
	scan_paths = []
	ge2_file_paths = []
	for sd in scan_subdirs:
		temp = path + sd + '/ff'
		scan_paths.append(temp)
	for path in scan_paths:
		for src, dirs, files in os.walk(path):
			for file in files:
				if(file.endswith('.ge2')):
					ge2_file_paths.append(os.path.join(src, file))
					
	return ge2_file_paths

def build_darkfield_file(darkfield_path):
	skip_lines = 4096
	darkfield_array = np.fromfile(darkfield_path, dtype = 'int16', sep = '')
	darkfield_array = darkfield_array[skip_lines:skip_lines + 2048*2048]
	return (darkfield_array)

def image_substraction(ge2_file_paths, darkfield_file):
	skip_lines = 4096
	frame_resolution = 2048 * 2048	
	averaged_subtracted_array = []
	scan_counter = 0
	for scan in ge2_file_paths:
		sliced_frames = []
		subtracted_frames = []
		scan_file = np.fromfile(scan, dtype = 'int16', sep = '')
		scan_file = scan_file[skip_lines:]
		sliced_frames = [scan_file[i:i + frame_resolution] for i in range(0, len(scan_file), frame_resolution)]
		print('Reading scan: ', ge2_file_paths[scan_counter])
		scan_counter += 1
		for frame in sliced_frames:
			subtracted_frames.append(np.subtract(frame, darkfield_file))
		average_frames = np.average(subtracted_frames, axis = 0)
		average_frames = average_frames.astype(int)
		average_frames = average_frames.reshape(2048, 2048)
		averaged_subtracted_array.append(average_frames)
		del scan_file, sliced_frames[:],  subtracted_frames[:]
		gc.collect()
	return averaged_subtracted_array

def display_single_scan(ge2_file_paths, subtract_scans, display_scan):
	display_scan = display_scan.lower()
	if(display_scan != 'n' or display_scan != '0'):
		for index, path in enumerate(ge2_file_paths):
			split_path = path.split('/')
			scan_number = split_path[len(split_path)-3]
			if(scan_number == display_scan):
				plt.imshow(subtract_scans[index])
				plt.show()
				break
	else:
		print('No scan to display.')

def save_processed_scans(destination_dir_path, scan_subdirs, subtract_scans, ge2_file_paths, ai, overwrite_files, file_type):
	overwrite_files = overwrite_files.lower()
	dest_subdirs_array = []
	for subdir in scan_subdirs:
		dest_subdir = destination_dir_path + str(subdir)
		dest_subdirs_array.append(dest_subdir)
		try:
			os.makedirs(dest_subdir)
		except:
			pass
	for i in range(0, len(subtract_scans)):
		img_diff = subtract_scans[i]
		if(file_type == 1):
			if(overwrite_files == 'y' or overwrite_files == '1'):
				print('Overwriting reduced .chi file from: ', ge2_file_paths[i])
				tth_file_path = dest_subdirs_array[i] + '/' + ge2_file_paths[i][-13:-4] + '.chi'
				try:
					os.remove(tth_file_path) 
				except:
					pass
				tth_data_x, tth_data_y = ai.integrate1d(img_diff, data_points, unit = '2th_deg')
				tth_combined_xy = np.vstack((tth_data_x, tth_data_y)).T
				np.savetxt(tth_file_path, tth_combined_xy)
			else:
				tth_file_path = dest_subdirs_array[i] + '/' + ge2_file_paths[i][-13:-4] + '.chi'
				if(os.path.exists(tth_file_path)):
					pass
				else:
					print('Reducing to .chi file from: ', ge2_file_paths[i])
					tth_data_x, tth_data_y = ai.integrate1d(img_diff, data_points, unit = '2th_deg')
					tth_combined_xy = np.vstack((tth_data_x, tth_data_y)).T
					np.savetxt(tth_file_path, tth_combined_xy)
		elif(file_type == 2):
			if(overwrite_files == 'y' or overwrite_files == '1'):
				print('Overwriting reduced .qda file from: ', ge2_file_paths[i])
				qda_file_path = dest_subdirs_array[i] + '/' + ge2_file_paths[i][-13:-4] + '.qda'
				try:
					os.remove(qda_file_path)
				except:
					pass
				qda_data_x, qda_data_y = ai.integrate1d(img_diff, data_points, unit = 'q_A^-1')
				qda_combined_xy = np.vstack((qda_data_x, qda_data_y)).T
				np.savetxt(qda_file_path, qda_combined_xy)
			else:
				qda_file_path = dest_subdirs_array[i] + '/' + ge2_file_paths[i][-13:-4] + '.qda'
				if(os.path.exists(qda_file_path)):
					pass
				else:
					print('Reducing to .qda file from: ', ge2_file_paths[i])
					qda_data_x, qda_data_y = ai.integrate1d(img_diff, data_points, unit = 'q_A^-1')
					qda_combined_xy = np.vstack((qda_data_x, qda_data_y)).T
					np.savetxt(qda_file_path, qda_combined_xy)
		elif(file_type == 3):
			if(overwrite_files == 'y' or overwrite_files == '1'):
				print('Overwriting reduced .chi file from: ', ge2_file_paths[i])
				tth_file_path = dest_subdirs_array[i] + '/' + ge2_file_paths[i][-13:-4] + '.chi'
				try:
					os.remove(tth_file_path) 
				except:
					pass
				tth_data_x, tth_data_y = ai.integrate1d(img_diff, data_points, unit = '2th_deg')
				tth_combined_xy = np.vstack((tth_data_x, tth_data_y)).T
				np.savetxt(tth_file_path, tth_combined_xy)
				print 'Overwriting reduced .qda file from: ', ge2_file_paths[i]
				qda_file_path = dest_subdirs_array[i] + '/' + ge2_file_paths[i][-13:-4] + '.qda'
				try:
					os.remove(qda_file_path)
				except:
					pass
				qda_data_x, qda_data_y = ai.integrate1d(img_diff, data_points, unit = 'q_A^-1')
				qda_combined_xy = np.vstack((qda_data_x, qda_data_y)).T
				np.savetxt(qda_file_path, qda_combined_xy)
			else:
				tth_file_path = dest_subdirs_array[i] + '/' + ge2_file_paths[i][-13:-4] + '.chi'
				qda_file_path = dest_subdirs_array[i] + '/' + ge2_file_paths[i][-13:-4] + '.qda'
				if(os.path.exists(tth_file_path)):
					pass
				else:
					print('Reducing to .chi file from: ', ge2_file_paths[i])
					tth_data_x, tth_data_y = ai.integrate1d(img_diff, data_points, unit = '2th_deg')
					tth_combined_xy = np.vstack((tth_data_x, tth_data_y)).T
					np.savetxt(tth_file_path, tth_combined_xy)
				if(os.path.exists(qda_file_path)):
					pass
				else:
					print('Reducing to .qda file from: ', ge2_file_paths[i])
					qda_data_x, qda_data_y = ai.integrate1d(img_diff, data_points, unit = 'q_A^-1')
					qda_combined_xy = np.vstack((qda_data_x, qda_data_y)).T
					np.savetxt(qda_file_path, qda_combined_xy)
		else:
			print('Could not create the reduced data files.')
			
#USER INPUT
root_dir_path =	input('Enter the path to the raw data directory: ')
start_scan_from = int(input('Start from scan number (type 0 to read all scans): '))
darkfield_file_path = input('Enter the path to the darkfield file: ')
darkfield_file_within = input('Is the darkfield file within the raw data directory (y/n): ')
destination_dir_path = input('Enter the path to the destinantion directory: ')
file_types = int(input('What files do you want to generate? (1:.chi / 2:.qda / 3:both): '))
overwrite_files = input('Do you want to overwrite the existing data reduction files? (y/n): ')
display_scan = input('Display a specific scan (type 'n' to skip this step): ')
print('========== Azimuthal Integration ==========')
data_points = int(input('Enter the number of data points per scan: '))
fit2d_x = float(input('Enter the horizontal pixel position for the main beam in milimeters: '))
fit2d_y = float(input('Enter the vertical pixel position for the main beam in milimeters: '))
fit2d_dist = float(input('Enter the distance from sample to detector in milimeters: '))
energy = float(input('Enter the energy of the X-Ray beam in KeV: '))

#STATIC DATA & CALCULATIONS
fit2d_dist = fit2d_dist / 1000
detector = pyFAI.detectors.Detector(200e-6, 200e-6)
detector.max_shape = (2048, 2048)
wl = 12.3984 / energy * 1e-10
p1 = (2048 - fit2d_y) * 200e-6
p2 = fit2d_x * 200e-6
rot1deg = 0
rot2deg = 0
rot3deg = 0
ai = pyFAI.AzimuthalIntegrator(wavelength = wl, dist = fit2d_dist, detector = detector, poni1 = p1, poni2 = p2, rot1 = np.radians(rot1deg), rot2 = np.radians(rot2deg), rot3 = np.radians(rot3deg))

raw_subdirs_list = get_subdirs(root_dir_path)
scan_subdirs = build_raw_subdirs(raw_subdirs_list, darkfield_file_path, start_scan_from, darkfield_file_within)
ge2_file_paths = build_scan_file_paths(root_dir_path, scan_subdirs)
darkfield_file = build_darkfield_file(darkfield_file_path)
subtract_scans = image_substraction(ge2_file_paths, darkfield_file)
save_processed_scans(destination_dir_path, scan_subdirs, subtract_scans, ge2_file_paths, ai, overwrite_files, file_types)
display_single_scan(ge2_file_paths, subtract_scans, display_scan)

del raw_subdirs_list, scan_subdirs, ge2_file_paths, darkfield_file, subtract_scans
gc.collect()