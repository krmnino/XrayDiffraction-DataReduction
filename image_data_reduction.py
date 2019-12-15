#####################################
#	image_data_subtraction.py 		
#	Python 3.x	
#	Kurt Manrique-Nino					
#####################################


import os
import matplotlib
import matplotlib.pyplot as plt

import numpy as np
import pyFAI
import pyFAI.calibrant
from pyFAI.calibrant import ALL_CALIBRANTS
import fabio
from pyFAI.multi_geometry import MultiGeometry


def get_subdirs(root):
	for src, dirs, files in os.walk(root):
		return dirs

def build_processed_subdirs(subdirs_list):
	sort_subdirs = []
	for sd in subdirs_list:
		try:
			temp = int(sd)
			sort_subdirs.append(temp)
		except:
			pass
	sort_subdirs.sort()
	sort_subdirs = list(map(str, results)) # for p3.x: list(map(int, results))
	return sort_subdirs

def build_txt_paths(root_dir_path, processed_subdirs):
	processed_paths = []
	txt_file_paths = []
	for sd in processed_subdirs:
		temp = root_dir_path + sd
		processed_paths.append(temp)
	for path in processed_paths:
		for src, dirs, files in os.walk(path):
			for file in files:
				if(file.endswith('txt')):
					txt_file_paths.append(os.path.join(src, file))				
	return txt_file_paths

def integration_function(txt_file_paths, ai):
	for i in range(0, len(txt_file_paths)):
		print('Reducing file: ', txt_file_paths[i]) 
		dest_path = txt_file_paths[i][:-4]
		tth_dest_path = dest_path + '.chi'
		qda_dest_path = dest_path + '.qda'
		img_diff = np.genfromtxt(txt_file_paths[i])
		tth_data_x, tth_data_y = ai.integrate1d(img_diff, data_points, unit = '2th_deg')
		tth_combined_xy = np.vstack((tth_data_x, tth_data_y)).T
		qda_data_x, qda_data_y = ai.integrate1d(img_diff, data_points, unit = 'q_A^-1')
		qda_combined_xy = np.vstack((qda_data_x, qda_data_y)).T
		np.savetxt(tth_dest_path, tth_combined_xy)
		np.savetxt(qda_dest_path, qda_combined_xy)

#USER INPUT
root_dir_path = input('Enter the path to the processed data directory: ')
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
processed_subdirs = build_processed_subdirs(raw_subdirs_list)
txt_file_paths = build_txt_paths(root_dir_path, processed_subdirs)
integration_function(txt_file_paths, ai)