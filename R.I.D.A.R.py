#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 08:18:13 2018

@author: jenkinscc
"""
import time
import os
import statistics


working_directory = os.getcwd()

file_list=[]

for root, dirs, files in os.walk(working_directory):
    for name in files:
        if '.mgf' in name:
            file_list.append(name)
        else:
            next
file_list.sort()

intensity_lists = []

'''Parses through the file and separates the scans from each other'''
def separate_scan_csv(name):      
    with open(name, 'r') as file:
        x = file.read().split('BEGIN IONS')
        return x[1:]

'''Pulls the information from the config.txt file and returns the variables from the file'''
def open_config_file(configuration_file):
    with open(configuration_file, 'r') as c:
        ions = []
        line = c.readlines()
        tolerance = float(line[0][10:-1])
        control_label = (line[1][12:-1])
        fold_change = float(line[2][12:-1])
        for reporter_ion_field in line[4:]:
            if len(reporter_ion_field) >= 1:
                ions.append(reporter_ion_field[:-1])
                intensity_lists.append(reporter_ion_field[:-1])
                intensity_lists.append([])
        c.close()
        return line, tolerance, control_label, fold_change, ions

line, tolerance, control_label, fold_change, ions = open_config_file('config.txt')

'''Sorts the reporter ions list in ascending order incase of input error from user'''
sorted(ions, key=float)   

'''Used for identification of average intensity of each reporter ion channel'''
for name in file_list:
    start =time.time() #Starts timer at first scan
    spectra_counter = 0 
    total_spectra = 0
    with open('Filtered_' + name, 'w') as f: #Opens up a new filtered file to write to
        f.writelines('MASS=Monoisotopic' + '\n')
        intdic = {}    #Creates the dictionary that will contain the intensitys of each channel 
        for reporter in ions: 
            intdic[reporter] = [] #Assigns the reporter ion to a key and assigns it to an open list that the intensities will occupy
        for MS1 in separate_scan_csv(name): 
            clean_MS1 = MS1.strip() #removes the whitespaces in the scan
            entry = clean_MS1.split('\n') #scan is made up of header and ions sp this splits them
            header = entry[0:5]
            scans = entry[5:-1]
            scanstring = '\n'.join(scans) #Since each ion is separated by a new line, we want to remove the new line
            scan_list = [i.split(' ') for i in scans] #the removal of the new line enables us to split the ions seen in the scan
            for reporter in ions: 
                for m_z in scan_list: #this part calculates the min an max of the mass of the observed reporter ions
                    reading = float(m_z[0])
                    intensity = float (m_z[1])
                    if reading > float(ions[-1]) + tolerance: #Speeds up the looping (looks at last value in ions from the sort before and if the mass is greater that its max value, it will skip to the next scan)
                        break
                    lower = float(reporter) - tolerance
                    upper = float(reporter) + tolerance
                    if lower <= reading <= upper:
                       intdic[reporter].append(intensity) #Appends the list of the reporter with the observed intensity value
        '''Below, a matrix of all ratios is created between the channels depending on the average intensity of each channel'''
        avg_list = [] #Creates an empty list that will contain average from each channel
        ratio_matrix = []
        for k, v in intdic.items():
            avg = statistics.mean(v) #takes average of all intensities in value
            avg_list.append(float(avg)) 
            intdic[k] = avg #re assigns the reporter ion key to the average value of the intensities for that channel
        '''These lines create a list that looks like [reporter, avg1/reporter_avg, avg2/reporter_avg, avg3/reporter_avg, avg4/reporter_avg]'''
        for k,v in intdic.items(): 
            ratios = []
            ratios.append(str(k))
            for average in avg_list:
                ratio = v/average
                #The below if, elif loop will adjust the ratios below 1 to their inverse for easier comparison later
                if ratio < 1:
                    ratios.append(1/ratio*fold_change)
                elif ratio >= 1:
                    ratios.append(ratio*fold_change)
            ratio_matrix.append(ratios)
        '''Go back in to the scans to pull out the features of the reporter ions in the scan'''    
        for MS1 in separate_scan_csv(name): 
            total_spectra += 1
            clean_MS1 = MS1.strip()
            entry = clean_MS1.split('\n')
            header = entry[0:5]
            scans = entry[5:-1]
            scanstring = '\n'.join(scans)
            scan_list = [i.split(' ') for i in scans]
            identified_list = [] #A list containing the reporter ions and the associated intensities in the scans
            control_label_intensity = []
            for m_z in scan_list:
                reading = float(m_z[0])
                intensity = float (m_z[1])
                if reading > float(ions[-1]) + tolerance:
                    break 
                for reporter in ions:
                    lower = float(reporter) - tolerance
                    upper = float(reporter) + tolerance
                    if lower <= reading <= upper:
                        identified_list.append([str(reporter), float(m_z[1])])
            '''This checks the amount of reporter ions found in the scan'''            
            reporters_found = []
            for identified_value in identified_list: #for each of the identified repoter ions and their intensities
                reporters_found.append(identified_value[0])
            if control_label in reporters_found: #If the reporter ion is not found, the script will not write to the filtered file
                if 1 <= len(reporters_found) < len(ions):
                    for reporters in ions:
                        if reporters not in reporters_found:
                            identified_list.append([reporters, 0])
                    identified_list.sort(key=lambda x: x[0]) #Sorts identified list by the reporter ions
                    
                ''' Creation of a comparison matrix of the observed values in the scan, comparing each channel to each other'''    
                comparison_matrix = []
                for identified in identified_list:
                    comp_value = float(identified[1]) # Pulls the intensity of the ion
                    comparisons = []
                    comparisons.append(identified[0])
                    for identified_intensity in identified_list:
                        try:
                            observed_ratio = float(identified_intensity[1])/comp_value #compares the value of each channel to the others
                            comparisons.append(observed_ratio)
                        except ZeroDivisionError:
                            observed_ratio = 0 # if a channel was empty, this handles the error and appends the ratio as a zero
                            comparisons.append(observed_ratio)
                    comparison_matrix.append(comparisons)
                '''This is where the comparison matrix and the ratio matrix are compared'''    
                sucess_counter = 0 # keeps track of how many successful comparisons that appear
                for observed_comparison in comparison_matrix:
                    x = comparison_matrix.index(observed_comparison)
                    for value in observed_comparison[1:]:
                        y = observed_comparison.index(value)
                        if value == 0:
                            sucess_counter += 1
                            continue
                        try:
                            ratio_matrix[x][y]
                            
                        except IndexError:
                            continue
                        
                        if value > ratio_matrix[x][y]:
                            sucess_counter += 1                    
                            
                if sucess_counter >= 1:
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

    end = time.time()                    
    with open('Meta' + name + '.txt', 'w') as q:
       q.writelines('Total spectra: ' + str(total_spectra) + '\n')
       q.writelines('Removed Spectra: ' + str(total_spectra - spectra_counter) + '\n')
       q.writelines('Time of filtering: ' + str(end - start) + '\n')
       q.writelines('Average intensity of channels:' + '\n' + str(ions) + '\n' + str (avg_list) + '\n')
       
                    
                        
                
        
                
            