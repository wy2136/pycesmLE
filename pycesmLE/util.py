'''
Wenchang Yang (yang.wenchang@uci.edu)
'''

def get_ensemble_datafiles(dataname, component='cam'):
    '''Get data files of the CESM-LE simulations for each ensemble member, as
    a dict. The keys are the ensemble member indices and the values are
    corresponding data files.'''
    
    members = list(range(1,36)) + list(range(101,106))
    ensemble_datafiles = {}
    for m in members:
        if component in ('cam', 'atm'):
            datafiles = [
                'b.e11.B20TRC5CNBDRD.f09_g16.{:03d}.cam.h0.{}.192001-200512.nc'.format(m, dataname),
                'b.e11.BRCP85C5CNBDRD.f09_g16.{:03d}.cam.h0.{}.200601-208012.nc'.format(m, dataname),
                'b.e11.BRCP85C5CNBDRD.f09_g16.{:03d}.cam.h0.{}.208101-210012.nc'.format(m, dataname),
            ]
        elif component in ('cice', 'ice'):
            datafiles = [
                'b.e11.B20TRC5CNBDRD.f09_g16.{:03d}.cice.h.{}.192001-200512.nc'.format(m, dataname),
                'b.e11.BRCP85C5CNBDRD.f09_g16.{:03d}.cice.h.{}.200601-208012.nc'.format(m, dataname),
                'b.e11.BRCP85C5CNBDRD.f09_g16.{:03d}.cice.h.{}.208101-210012.nc'.format(m, dataname),
            ]
        if m == 1:
            # the first member historical run covers period 1850-2005
            datafiles[0] = datafiles[0].replace('192001', '185001')
        if m > 33:
            # members 1-33 each includes two seperate data files (2006-2080
            # and 2081-2100) for RCP8.5 experiment, others (34-40 and 101-105)
            # only include a single data file (2006-2100)
            datafiles.pop()
            datafiles[1] = datafiles[1].replace('208012', '210012')

        ensemble_datafiles[m] = datafiles

    return ensemble_datafiles
