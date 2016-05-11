#!/usr/bin/python3.4

import pysysp
import pyfits

import numpy as np
from pathlib import Path,PurePosixPath

#load a spectrum from a fits file
#vega = pysysp.StarSpectrum('alpha_lyr_stis_006.fits')

def parse_miles_spectra(filename=None):
	if filename is None: 
		print("void MILES spectra filename")
		return None
	fit1 = pyfits.open('../miles/Mbi1.30Zp0.40T14.0000_iTp0.40_Ep0.40.fits')
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

#synt='../miles/Mbi1.30Zp0.40T14.0000_iTp0.40_Ep0.40.fits'
#miles_spectra = pysysp.StarSpectrum(synt)

def parse_miles():
	miles_spectra = []
	miles_path = Path('../miles/')
	count = 0
	for miles_file in miles_path.iterdir():
		suffix = PurePosixPath(miles_file).suffix
		path = str(miles_file)
		#print(path, suffix)
		if miles_file.is_file() and suffix=='.fits':
			miles_params = parse_miles_spectra('../miles/%s' % miles_file)
			miles_spectra.append((pysysp.StarSpectrum(path),miles_params))
			count += 1
			if count % 10: 
				print('.', end='', flush=True)
			else:
				print(count, end='', flush=True)
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
	shards_band = []
	shards_path = Path('../shards/')
	for shard_file in shards_path.iterdir(): 
		if shard_file.is_file() and PurePosixPath(shard_file).suffix=='.res':
			shards_band.append(pysysp.BandPass('../shards/%s' % shard_file))
	shards = sorted(shards_band, key=lambda b: np.max(b.wavelength))
	return shards

# Compute band magnitudes for a given spectra
def compute_response(shards, spectra):
	resp=[]
	for band in shards:
		mag=0
		try:	
			mag=spectra.apmag(band,mag='AB',mzero=0.0)
		except ValueError:
			pass
		resp.append((np.max(band.wavelength),mag))
	for a,b in resp: print(a,b)

# Put all together
shards_data = parse_shard()
miles_spectra = parse_miles()
for (s,pp) in miles_spectra:
	print(pp)
	compute_response(shards_data, s) 
