#!/usr/bin/python3.4

import pysysp
import pyfits

#load a spectrum from a fits file
#vega = pysysp.StarSpectrum('alpha_lyr_stis_006.fits')



def miles_parse(filename=None):
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

synt='../miles/Mbi1.30Zp0.40T14.0000_iTp0.40_Ep0.40.fits'
miles_spectra = pysysp.StarSpectrum(synt)
miles_params = miles_parse(synt)

#print the flux
print(miles_spectra.flux)

#Check available filters
#print(pysysp.showfilters)

#load the photonic response for the bands B and V with linear smoothing
#V=pysysp.BandPass('V',smt='linear')
#B=pysysp.BandPass('B',smt='linear')
#print(V)
#print(B)

#You can also load any ascii file with two columns (first wavelength, second filter response)
S = pysysp.BandPass('../shards/shards_f602w17.res')
print(miles_spectra.apmag(S,mag='AB',mzero=0.0))
print(miles_spectra.apmag(S,mag='Vega',mzero=0.03))


