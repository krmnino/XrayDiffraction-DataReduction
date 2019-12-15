#####################################
#	image_subtraction.py 			
#	Python 3.x	
#	Kurt Manrique-Nino					
#####################################

import numpy as np
import gc
import os

def get_subdirs(root):
	for src, dirs, files in os.walk(root):
		return dirs

def build_raw_subdirs(subdirs_list, darkfield_scan):
	sort_subdirs = []
	for sd in subdirs_list:
		try:
			temp = int(sd)
			if(temp != darkfield_scan):
				sort_subdirs.append(temp)
		except:
			pass
	sort_subdirs.sort()
	sort_subdirs = list(map(str, results))
	return(sort_subdirs)

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

def build_darkfield_file_path(path, darkfield_scan):
	darkfield_path = path + str(darkfield_scan) + '/ff'
	for src, dirs, files in os.walk(darkfield_path):
		for file in files:
			if(file.endswith('ge2')):
				return os.path.join(src, file)
			else:
				print('.ge2 darkfield image not found')

def build_darkfield_file(darkfield_path):
	skip_lines = 4096
	darkfield_array = np.fromfile(darkfield_path, dtype = 'int16', sep = '')
	darkfield_array = darkfield_array[skip_lines:skip_lines + 2048*2048]
	return (darkfield_array)

def image_substraction(ge2_file_paths, darkfield_file):
	skip_lines = 4096
	frame_resolution = 2048 * 2048	
	ge2_file_array = []
	for scan in ge2_file_paths:
		sliced_frames = []
		subtracted_frames = []
		scan_file = np.fromfile(scan, dtype = 'int16', sep = '')
		scan_file = scan_file[skip_lines:]
		sliced_frames = [scan_file[i:i + frame_resolution] for i in range(0, len(scan_file), frame_resolution)]
		scan_counter += 1
		print('Reading scan: ', scan)
		for frame in sliced_frames:
			subtracted_frames.append(np.subtract(frame, darkfield_file))
		average_frames = np.average(subtracted_frames, axis = 0)
		average_frames = average_frames.astype(int)
		average_frames = average_frames.reshape(2048, 2048)
		ge2_file_array.append(average_frames)
		del scan_file, sliced_frames[:],  subtracted_frames[:]
		gc.collect()
	return ge2_file_array

def save_processed_scans(destination_dir_path, scan_subdirs, subtract_files, ge2_file_paths):
	dest_subdirs_array = []
	full_dest_subdirs_array = []
	for subdir in scan_subdirs:
		dest_subdir = destination_dir_path + str(subdir)
		dest_subdirs_array.append(dest_subdir)
		os.makedirs(dest_subdir)
	for i in range(0, len(ge2_file_paths)):
		ge2_path = ge2_file_paths[i]
		name = ge2_path[len(ge2_path) - 13:len(ge2_path) - 4] + '.txt'
		full_path = '/' + dest_subdirs_array[i] + '/' + name
		full_dest_subdirs_array.append(full_path)
	for i in range(0, len(full_dest_subdirs_array)):
		np.savetxt(full_dest_subdirs_array[i], subtract_files[i], delimiter = ' ', fmt = '%.0f')

root_dir_path =	input('Enter the path to the raw data directory: ')
darkfield_scan = int(input('Enter the scan number with the darkfield scan: '))
destination_dir_path = input('Enter the path to the destinantion directory: ')

raw_subdirs_list = get_subdirs(root_dir_path)
scan_subdirs = build_raw_subdirs(raw_subdirs_list, darkfield_scan)
ge2_file_paths = build_scan_file_paths(root_dir_path, scan_subdirs)
darkfield_path = build_darkfield_file_path(root_dir_path, darkfield_scan)
darkfield_file = build_darkfield_file(darkfield_path)
subtract_files = image_substraction(ge2_file_paths, darkfield_file)
save_processed_scans(destination_dir_path, scan_subdirs, subtract_files, ge2_file_paths)