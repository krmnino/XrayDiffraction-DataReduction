####################################
#	single_image_subtraction_v2 	
#	Python 3.x		
#	Kurt Manrique-Nino				
####################################

import numpy as np
import gc
import os

def build_darkfield_file(darkfield_path):
	skip_lines = 4096
	darkfield_array = np.fromfile(darkfield_path, dtype = 'int16', sep = '')
	darkfield_array = darkfield_array[skip_lines:skip_lines + 2048*2048]
	return (darkfield_array)

def image_substraction(ge2_file_path, darkfield_file):
	skip_lines = 4096
	frame_resolution = 2048 * 2048	
	scan_file = np.fromfile(ge2_file_path, dtype = 'int16', sep = '')
	scan_file = scan_file[skip_lines:]
	sliced_frames = [scan_file[i:i + frame_resolution] for i in range(0, len(scan_file), frame_resolution)] 
	subtracted_frames = []
	for frame in sliced_frames:
		subtracted_frames.append(np.subtract(frame, darkfield_file))
	average_frames = np.average(subtracted_frames, axis = 0)
	average_frames = average_frames.astype(int)
	average_frames = average_frames.reshape(2048, 2048)
	del scan_file, sliced_frames[:],  subtracted_frames[:]
	gc.collect()
	return average_frames

def save_processed_scans(subtracted_file, destination_dir_path, scan_file_path):
	name = scan_file_path[len(scan_file_path) - 13:len(scan_file_path) - 4] + '.txt'
	full_path = destination_dir_path + name
	np.savetxt(full_path, subtracted_file, delimiter = ' ', fmt = '%.0f')

scan_file_path = input('Enter the path to the .ge2 file: ')
darkfield_path = input('Enter the path to the dark field file: ')
destination_dir_path = input('Enter the path to the destinantion directory: ')

darkfield_file = build_darkfield_file(darkfield_path)
subtracted_file = image_substraction(scan_file_path, darkfield_file)
save_processed_scans(subtracted_file, destination_dir_path, scan_file_path)