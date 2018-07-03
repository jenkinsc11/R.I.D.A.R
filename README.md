# Reporter Ion Filter for Proteomics
This little piece of code filters through all of the MS1 scans of an MGF file to identify if all of the associated reporter ions are present. If the reporter ions are present then a fold change identification is run. If the fold change is higher than the set threshold, the entire MS1 will be written to a new MGF file that decreases the search time and file size when compared to the original file. This ensures that scans that cannot be quantified are removed and the overall file is de-cluttered.

# Running the Script
In order to run this script, a config.txt file must be stored in the working directory in the specific format. This is where you will specify the m/z values of your reporter ions, the m/z tolerance, which ion is your control ion and the fold change threshold. The script will read the values in the config file. Within the config file, you can add as many reporter ion m/z values as you want below the line that reads $$$ Place Reporter Ions Below This Line $$$. The Script will search through all of the files below your working directory and create filtered versions of .MGF files without changing the initial .MGF file. In my experiances, the memory usage hovers around 4GB when the filtering is taken place so I recommend at least 8 GB of RAM. Python 3.6 or greater is required.

# Help
Please do not to hesitate to contact me if you have trouble running this script at:
conor.jenkins@outlook.com
