#!C:\Users\jenkinscc\anaconda\python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 12:51:00 2018

@author: jenkinscc
"""
filename = 'test_data.mgf'

config = 'config.txt'

with open(config, 'r') as c:
    line = c.readlines()
    rep_1 = line[0][16:]
    rep_2 = line[1][16:]
    rep_3 = line[2][16:]
    rep_4 = line[3][16:]
    control_label = float(line[5][13:])
    tolerance = float(line[4][10:])
    fold_change = int(line[6][12:])
    c.close()

ions = (rep_1, rep_2, rep_3, rep_4)


def separate_scan_csv(filename):      
    with open(filename) as file:
        x = file.read().split('BEGIN IONS')
        return x[1:] #returns all the lines after MASS=Monoisotopic
    
total_spectra = 0
spectra_counter = 0
    
with open('Filtered_' + filename, 'w') as f:
 f.writelines('MASS=Monoisotopic' + '\n')    
 for value in separate_scan_csv(filename): 
    total_spectra +=1
    counter = 0 #counts the number of matches of reporter ions
    x = value.strip()
    entry = x.split('\n')
    header = entry[0:5]
    scans = entry[5:-1]
    scanstring = '\n'.join(scans)
    scan_list = [i.split(' ') for i in scans]
    intensity_list= []
    control_label_intensity = []
    for m_z in scan_list:
        reading = float(m_z[0]) 
        for reporter in ions:
            lower = float(reporter) - tolerance
            upper = float(reporter) + tolerance
            if lower <= reading <= upper:
                counter +=1
                intensity_list.append(float(m_z[1]))
        if control_label - tolerance <= reading <= control_label + tolerance:
            control_label_intensity.append(float(m_z[1]))
    if counter == len(ions): 
        spectra_counter += 1
        fold_change_counter = 0
        for value in intensity_list:
            for control in control_label_intensity:
                if value/control >= fold_change:
                    fold_change_counter +=1
        if fold_change_counter >= 1: 
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
                    
print('I found', total_spectra, 'spectra!','\n\n', 'I removed', total_spectra - spectra_counter, 'spectra','\n\n', spectra_counter, 'spectra meet qualifications')
    