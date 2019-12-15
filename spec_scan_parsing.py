#####################################
#	spec_scan_parsing.py 		
#	Python 3.x					
#	Kurt Manrique-Nino	
#####################################

import numpy as np 

def skip_header_lines(root_path):
	with open(root_path) as file:
		skip_header = 0
		for index, line in enumerate(file):
			line_splited = line.split(' ')
			if(line_splited[0] == '#S'):
				skip_header = index
				break
		file.close()
	return skip_header

def range_of_lines(root_path, skip_header):
	lines_start = []
	lines_end = []
	with open(root_path) as file:
		last_line = 0
		for index, line in enumerate(file):
			last_line = index
			if(index > skip_header):
				line_splited = line.split(' ')
				if(line_splited[0] == '#L'):
					lines_start.append(index - 1)
				if(line_splited[0] == '#S'):
					lines_end.append(index - 1)
	last_line += 1
	lines_end.append(last_line)
	range_lines = np.vstack((lines_start, lines_end))
	file.close()
	return range_lines

def scans_from_file(root_path, range_lines):
	file_arr = []
	for i in range(0, len(range_lines[0])):
		scan = []
		with open(root_path) as file: 
			for index, line in enumerate(file):
				if(index > range_lines[0][i]):
					if('#L' in line or '#' not in line):
						scan.append(line[:-1])
				if(index == range_lines[1][i]):
					break
			file.close()
		file_arr.append(scan)
	return file_arr

def generate_scan_names(root_path, scans, output_path):
	file_paths = []
	with open(root_path) as file:
		for line in file:
			if('#S' in line):
				line_splited = line.split(' ')
				file_paths.append(output_path + '/S' + line_splited[1] + '.txt')
	for index, path in enumerate(file_paths):
		np.savetxt(path, scans[index], fmt = '%s') 
		file.close()

root_path = input('Enter the SPEC log file path: ')
output_path = input('Enter the output directory path: ')

skip_header = skip_header_lines(root_path)
range_lines = range_of_lines(root_path, skip_header)
scans = scans_from_file(root_path, range_lines)
generate_scan_names(root_path, scans, output_path)
