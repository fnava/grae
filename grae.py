#!/usr/bin/python3.4

import pysysp
import pyfits
import os.path
import json
import numpy as np
from pathlib import Path,PurePosixPath

#load a spectrum from a fits file
#vega = pysysp.StarSpectrum('alpha_lyr_stis_006.fits')

def parse_miles_spectra(filename=None):
	if filename is None: 
		print("void MILES spectra filename")
		return None
	fit1 = pyfits.open(filename)
	cards = fit1[0].header
	fit1.close()
	params = {
		'Model':		"# Models Library:",
		'Isochrone':		"# Isochrone:",
		'IMF':			"# IMF, Slope:",
		'Age':			"# Age \(Gyr\):",
		'MH':			"# \[M\/H\]:",
		'alphaFe':		"# \[alpha\/Fe\]:",
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
					value = m.group(2)
					#print(value)
					if k == 'IMF':
						r = re.compile('(..), *(.*)')
						n = r.match(value)
						if n is not None:
							values['IMF']=(n.group(1))
							values['slope']=(n.group(2))
					else:
						values[k]=value
	return values

#synt='../miles/Mbi1.30Zp0.40T14.0000_iTp0.40_Ep0.40.fits'
#miles_spectra = pysysp.StarSpectrum(synt)

def parse_miles2():
	""" Generate a nested dict:
	miles_spectra = {Model:,Isochrone:,IMF:} = [spectra, {slope:,Age:...}]
	"""
	miles_spectra = {}
	miles_path = Path('../miles/MILES/')
	count = 0
	for miles_file in miles_path.iterdir():
		suffix = PurePosixPath(miles_file).suffix
		path = str(miles_file)
		#print(path, suffix)
		if miles_file.is_file() and suffix=='.fits':
			#miles_params = parse_miles_spectra('../miles/MILES/%s' % miles_file)
			allpars = parse_miles_spectra('%s' % miles_file)
			pars = [ allpars['Model'],
				allpars['Isochrone'],
				allpars['IMF']
				]
			if not pars[0] in miles_spectra:
				miles_spectra[pars[0]] = {}
			if not pars[1] in miles_spectra[pars[0]]:
				miles_spectra[pars[0]][pars[1]] = {}
			if not pars[2] in miles_spectra[pars[0]][pars[1]]:
				miles_spectra[pars[0]][pars[1]][pars[2]] = {}
			miles_spectra[pars[0]][pars[1]][pars[2]] = [pysysp.StarSpectrum(path),allpars]
			count += 1
			if count % 10: 
				print('.', end='', flush=True)
			else:
				print('{0:4d}'.format(count), end='', flush=True)
		#if count > 100: break
	#shards = sorted(shards_band, key=lambda b: np.max(b.wavelength))
	return miles_spectra

def parse_miles():
	miles_spectra = []
	miles_path = Path('../miles/MILES/')
	count = 0
	for miles_file in miles_path.iterdir():
		suffix = PurePosixPath(miles_file).suffix
		path = str(miles_file)
		#print(path, suffix)
		if miles_file.is_file() and suffix=='.fits':
			#miles_params = parse_miles_spectra('../miles/MILES/%s' % miles_file)
			miles_params = parse_miles_spectra('%s' % miles_file)
			miles_spectra.append((pysysp.StarSpectrum(path),miles_params))
			count += 1
			if count % 10: 
				print('.', end='', flush=True)
			else:
				print('{0:4d}'.format(count), end='', flush=True)
		if count > 100: break
	#shards = sorted(shards_band, key=lambda b: np.max(b.wavelength))
	return miles_spectra

#print the flux
#print(miles_spectra.flux)

#Check available filters
#print(pysysp.showfilters)

#load the photonic response for the bands B and V with linear smoothing
#V=pysysp.BandPass('V',smt='linear')
#B=pysysp.BandPass('B',smt='linear')
#print(V)
#print(B)

#You can also load any ascii file with two columns (first wavelength, second filter response)
#S = pysysp.BandPass('../shards/shards_f602w17.res')
#print(miles_spectra.apmag(S,mag='AB',mzero=0.0))
#print(miles_spectra.apmag(S,mag='Vega',mzero=0.03))

# Parse all SHARD band responses:
def parse_shard():
	# Reading data back
	with open('shards.json', 'r') as f:
		shards_filters = json.load(f)
	shards_band = []
	shards_path = Path('../shards/')
	for filter in shards_filters: 	
	#for shard_file in shards_path.iterdir(): 
		filter_filename = 'shards_'+filter['Filter'].lower()+'.res'
		filter_filepath = os.path.join('../shards/', filter_filename)
		if os.path.isfile(filter_filepath):
			shards_band.append(pysysp.BandPass(filter_filepath))
	shards = sorted(shards_band, key=lambda b: np.max(b.wavelength))
	return shards

# Compute band magnitudes for a given spectra
def compute_response(shards, spectra):
	resp_row=[]
	for band in shards:
		mag=0
		try:	
			#mag=spectra.apmag(band,mag='nolog',mzero=0.0)
			mag=spectra.apmag(band,mag='AB',mzero=0.0)
		except ValueError:
			pass
		#resp_row.append((np.max(band.wavelength),mag))
		resp_row.append(mag)
	 #for a,b in resp: print(a,b)
	return resp_row

# Put all together
print("Parsing SHARDS filters data...", end='', flush=True)
shards_data = parse_shard()
print("done.", flush=True)
print("Parsing MILES SSP spectra files...", end='', flush=True)
miles_spectra = parse_miles()
print("done.", flush=True)

print("Computing SHARD responses...", end='', flush=True)
keys = [ 'Model', 'Isochrone', 'IMF',
	'slope', 'Age', 'MH', 'alphaFe', 'Version', 'Redshift']
first_row = list(keys)
for b in shards_data:
	first_row.append(np.min(b.wavelength))

resp = []
resp.append(first_row)
row = []
for (spectra,pars) in miles_spectra:
	for k in keys:
		row.append(pars[k])
	row += compute_response(shards_data, spectra) 
	resp.append(row)
print("done.", flush=True)


import csv
spamWriter = csv.writer(open('shardsout.csv', 'w'), delimiter=',',
		quotechar='"', quoting=csv.QUOTE_MINIMAL)
for r in resp:
	spamWriter.writerow(r)

import pickle
with open('shardsout.pickle', 'wb') as f:
	pickle.dump(resp, f)
