#!/usr/bin/python3.4

import pysysp
import pyfits
import json
import os.path
import numpy as np
from pathlib import Path,PurePosixPath

def parse_miles_spectra(filename=None):
	if filename is None: 
		print("void MILES spectra filename")
		return None
	fit1 = pyfits.open(filename)
	cards = fit1[0].header
	params = {
		'Models Library':	"# Models Library:",
		'IMF':			"# IMF, Slope:",
		'Age':			"# Age \(Gyr\):",
		'MH':			"# \[M\/H\]:",
		'alphaFe':		"# \[alpha\/Fe\]:",
		'Isochrone':		"# Isochrone:",
		'Version': 		"# Version:",
		'Redshift':		"# Redshift \(z\):"
		}

	values = {}
	import re

	for c,l in cards.items():
		if c == 'COMMENT':
			for k,v in params.items():
				r = re.compile('= \'(%s *) (.*)\'' % v)
				#print(r)
				m = r.match(l)
				if m is not None: 
					#print(m.group(2))
					values[k]=m.group(2)

	return values

def parse_miles():
	target = 356
	miles_spectra = []
	miles_path = Path('../miles/MILES/')
	count = 0
	for miles_file in miles_path.iterdir():
		suffix = PurePosixPath(miles_file).suffix
		path = str(miles_file)
		#print(path, suffix)
		if miles_file.is_file() and suffix=='.fits':
			if count == target:
				miles_params = parse_miles_spectra('%s' % miles_file)
				miles_spectra.append((pysysp.StarSpectrum(path),miles_params))
				break
			count += 1
			if count % 10: 
				print('.', end='', flush=True)
			else:
				print('{0:4d}'.format(count), end='', flush=True)
	#shards = sorted(shards_band, key=lambda b: np.max(b.wavelength))
	return miles_spectra

# Parse all SHARD band responses:
def parse_shard():
        # Reading data back
        with open('shards.json', 'r') as f:
                shards_filters = json.load(f)
        shards_path = Path('../shards/')
        for filter in shards_filters:
        #for shard_file in shards_path.iterdir():
                filter_filename = 'shards_'+filter['Filter'].lower()+'.res'
                filter_filepath = os.path.join('../shards/', filter_filename)
                if os.path.isfile(filter_filepath):
                        filter['band'] = pysysp.BandPass(filter_filepath)
        return shards_filters

# Compute band magnitudes for a given spectra
def compute_response(shards, spectra):
	resp_row=([],[],[],[])
	for filter in shards:
		band = filter['band']
		mag=0
		try:	
			mag=spectra.apmag(band,mag='nolog',mzero=0.0)
			#mag=spectra.apmag(band,mag='AB',mzero=0.0)
		except ValueError:
			pass
		bc = 10.0 * float(filter['CWL'])
		width = 10.0 *float(filter['Width'])
		resp_row[0].append( bc )
		resp_row[1].append( mag )
		resp_row[2].append( width/2 )
		resp_row[3].append( width/2 ) 
	 #for a,b in resp: print(a,b)
	return resp_row

# Put all together
shards_data = parse_shard()
miles_spectra = parse_miles()

first_row = list(miles_spectra[0][1].keys())
for b in shards_data:
	first_row.append(np.min(b['band'].wavelength))
resp = []
resp.append(first_row)

for (s,pp) in miles_spectra:
	row = list(pp.values())
	row += compute_response(shards_data, s) 
	resp.append(row)

import matplotlib.pyplot as plt

plt.figure(1, figsize=(4, 3))
plt.clf()
#plt.axes([.2, .2, .7, .7])
s = miles_spectra[-1][0]
print(s.flux)
plt.plot(s.wavelength, s.flux, linewidth=1, color='red')
r = compute_response(shards_data, s)
print(r)
plt.errorbar(r[0], r[1], xerr=[r[2], r[3]], linewidth=2, fmt='o', color='blue')
plt.yscale('log')	
#plt.axis('tight')
#plt.xlabel('n_components')
#plt.ylabel('explained_variance_')
plt.show()



