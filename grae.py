#!/usr/bin/python3.4

import pysysp

#load a spectrum from a fits file
#vega = pysysp.StarSpectrum('alpha_lyr_stis_006.fits')
syn1 = pysysp.StarSpectrum('../miles/Mbi1.30Zp0.40T14.0000_iTp0.40_Ep0.40.fits')

#print the flux
print(syn1.flux)

#Check available filters
#print(pysysp.showfilters)

#load the photonic response for the bands B and V with linear smoothing
#V=pysysp.BandPass('V',smt='linear')
#B=pysysp.BandPass('B',smt='linear')
#print(V)
#print(B)

#You can also load any ascii file with two columns (first wavelength, second filter response)
S = pysysp.BandPass('../shards/shards_f602w17.res')
print(syn1.apmag(S,mag='AB',mzero=0.0))

#compute the V magnitude in Vega system
#The magnitude of Vega in V band is not 0, so in order to
#compute the correct value we should correct the zero point
print(vega.apmag(V,mag='Vega',mzero=0.03))

#Same in AB system
print(vega.apmag(V,mag='AB'))


#Compute E(B-V) for a (monochromatic) extinction Av=0.5
ab=vega.extinction(B,law='cardelli',A=0.5,Rv=3.1)
av=vega.extinction(V,law='cardelli',A=0.5,Rv=3.1)
print(ab-av)
