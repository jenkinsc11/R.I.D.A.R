#!C:\Users\jenkinscc\anaconda\python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  1 12:10:17 2018

@author: jenkinscc
"""

import os

working_directory = os.getcwd()

file_list=[]

for root, dirs, files in os.walk(working_directory):
    for name in files:
        if '.mgf' in name:
            file_list.append(name)
        else:
            next

def separate_scan_csv(name):      
    with open(name) as file:
        x = file.read().split('BEGIN IONS')
        return x[1:]

#filename = 'WHIM02_18_14_20_IR_W_BI_20131209_H-PM_fA.mgf'

re_entered_spectra = 0    
total_spectra = 0
spectra_counter = 0

ions = []

with open('config_tester.txt', 'r') as c:
        line = c.readlines()
        tolerance = float(line[0][10:-1])
        control_label = float(line[1][12:-1])
        fold_change = float(line[2][12:-1])
        for reporter_ion_field in line[4:]:
            if len(reporter_ion_field) >= 1:
                ions.append(reporter_ion_field[:-1])
        c.close()

for name in file_list:
 with open('Filtered_' + name, 'w') as f:
  f.writelines('MASS=Monoisotopic' + '\n')    
  for MS1 in separate_scan_csv(name): 
    total_spectra +=1
    counter = 0 #counts the number of matches of reporter ions
    clean_MS1 = MS1.strip()
    entry = clean_MS1.split('\n')
    header = entry[0:5]
    scans = entry[5:-1]
    scanstring = '\n'.join(scans)
    scan_list = [i.split(' ') for i in scans]
    reporter_list = []
    intensity_list = []
    control_label_intensity = []
    for m_z in scan_list:
        reading = float(m_z[0]) 
        for reporter in ions:
            lower = float(reporter) - tolerance
            upper = float(reporter) + tolerance
            if lower <= reading <= upper:
                counter +=1
                reporter_list.append(reporter)
                intensity_list.append(float(m_z[1]))
        if control_label - tolerance <= reading <= control_label + tolerance:
            control_label_intensity.append(float(m_z[1]))
    if counter == len(ions): 
        fold_change_counter = 0
        for value in intensity_list:
            for control in control_label_intensity:
                if value/control >= fold_change or value/control <= 1/fold_change:
                    fold_change_counter +=1
        if fold_change_counter >= 1: 
                    spectra_counter += 1
                    print('Writing Spectra ', header[0])
                    f.writelines('BEGIN IONS' + '\n')
                    f.writelines(header[0] + '\n')
                    f.writelines(header[1] + '\n')
                    f.writelines(header[2] + '\n')
                    f.writelines(header[3] + '\n')
                    f.writelines(header[4] + '\n')
                    f.writelines(scanstring)
                    f.writelines('\n')
                    f.writelines('END IONS' + '\n' + '\n')
    if counter < 4 and counter >= 1:
        spectra_counter += 1
        re_entered_spectra += 1
        for value in ions:
            if value not in reporter_list:
                value.strip()
                re_entry = [value, '1']
                scan_list.append(re_entry)       
        scan_list.sort(key=lambda m_z: m_z[0])
        print('Writing Spectra reentry', header[0])
        f.writelines('BEGIN IONS' + '\n')
        f.writelines(header[0] + '\n')
        f.writelines(header[1] + '\n')
        f.writelines(header[2] + '\n')
        f.writelines(header[3] + '\n')
        f.writelines(header[4] + '\n')
        for item in scan_list:
            f.writelines(item[0] + ' ' + item[1] + '\n')
        f.writelines('\n')
        f.writelines('END IONS' + '\n' + '\n')
                        
 print('I found', total_spectra, 'spectra!\n', 'I re-entered',
      re_entered_spectra, 'spectra\n', 'I removed',
      total_spectra - spectra_counter, 'spectra\n', 
      spectra_counter, 'spectra meet qualifications')