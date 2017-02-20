## OUTPUT FUNCTIONS
# PART1: STORE DATA in netCDF4 file (output__nc_ini,output_nc,output_nc_fin)
# PART2: STORE INFO in txt file (output_txt_ini, ...
# PART3: STORE PARAMETERS IN .NPY FILE

## STORE DATA
def output_nc_ini():
    """ Initialise the netCDF4 file."""
    
    param['output_i'] = 0   # output index
        
    # store files, dimensions and variables in dictionnaries
    ncu = dict()
    ncv = dict()
    nch = dict()

    # creating the netcdf files
    ncu['file'] = Dataset(param['output_runpath']+'/u.nc','w')
    ncv['file'] = Dataset(param['output_runpath']+'/v.nc','w')
    nch['file'] = Dataset(param['output_runpath']+'/h.nc','w')
    
    # write general attributes
    for ncfile in [ncu,ncv,nch]:
        ncfile['file'].history = 'Created ' + tictoc.ctime(tictoc.time())
        ncfile['file'].description = 'Data from: Shallow-water model in double gyre configuration.'
        ncfile['file'].details = 'Cartesian coordinates, beta-plane approximation, Arakawa C-grid'
        ncfile['file'].resolution = '%i x %i grid points' % (param['nx'],param['ny'])
        ncfile['file'].domain_size = '%ikm x %ikm' % (param['Lx']*1e-3,param['Ly']*1e-3 )
        ncfile['file'].dx_dy = 'dx = '+str(param['dx']*1e-3)+'km, dy = '+str(param['dy']*1e-3)+'km'
        ncfile['file'].centered_latitude = str(param['lat_0'])+' deg N'
        ncfile['file'].time_step = 'dt = %.4fs' % param['dt']
        ncfile['file'].integration_length = '%.1idays' % (param['Nt']*param['dt']/3600./24.)
        ncfile['file'].integratin_steps = param['Nt']
        ncfile['file'].time_scheme = param['scheme']
        ncfile['file'].cfl_number = param['cfl']
        ncfile['file'].nc_restart_from_run = param['init_run_id']
        
    # create dimensions
    ncu['xdim'] = ncu['file'].createDimension('x',param['nx']-1)
    ncu['ydim'] = ncu['file'].createDimension('y',param['ny'])
    ncu['tdim'] = ncu['file'].createDimension('t',None)      # time is unlimited dimension

    ncv['xdim'] = ncv['file'].createDimension('x',param['nx'])
    ncv['ydim'] = ncv['file'].createDimension('y',param['ny']-1)
    ncv['tdim'] = ncv['file'].createDimension('t',None)      # time is unlimited dimension
    
    nch['xdim'] = nch['file'].createDimension('x',param['nx'])
    nch['ydim'] = nch['file'].createDimension('y',param['ny'])
    nch['tdim'] = nch['file'].createDimension('t',None)      # time is unlimited dimension
    
    # create variables
    p = 'f4' # precision
    fill_value = -999999
    for ncfile,var in zip([ncu,ncv,nch],['u','v','h']):
        ncfile['t'] = ncfile['file'].createVariable('t',p,('t',),zlib=True,fletcher32=True)
        ncfile['x'] = ncfile['file'].createVariable('x',p,('x',),zlib=True,fletcher32=True)
        ncfile['y'] = ncfile['file'].createVariable('y',p,('y',),zlib=True,fletcher32=True)
        ncfile[var] = ncfile['file'].createVariable(var,p,('t','y','x'),fill_value=fill_value,zlib=True,fletcher32=True)
    
    # write units
    for ncfile in [ncu,ncv,nch]:
        ncfile['t'].units = 's'
        ncfile['t'].fullname = 'time'
        ncfile['x'].units = 'm'
        ncfile['x'].fullname = 'spatial dimension x'
        ncfile['y'].units = 'm'
        ncfile['y'].fullname = 'spatial dimension y'
    
    ncu['u'].units = 'm/s'
    ncv['v'].units = 'm/s'
    nch['h'].units = 'm'
    
    ncu['u'].missing_value = fill_value
    ncv['v'].missing_value = fill_value
    nch['h'].missing_value = fill_value

    # write dimensions
    for ncfile,var in zip([ncu,ncv,nch],['u','v','T']):
        ncfile['x'] = param['x_'+var]
        ncfile['y'] = param['y_'+var]
        
    # make globally available
    global ncfiles
    ncfiles = [ncu,ncv,nch]
    
    output_txt('Output will be stored in '+param['runfolder']+' every %i hours.' % (param['output_dt']/3600.))
    
    
def output_nc(u,v,h,t):
    """ Extend u,v,h fields on every nth time step """
    # output index j
    j = param['output_i']   # for convenience

    for ncfile in ncfiles:
        ncfile['t'][j] = t
    
    ncfiles[0]['u'][j,:,:] = u2mat(u)
    ncfiles[1]['v'][j,:,:] = v2mat(v)
    ncfiles[2]['h'][j,:,:] = h2mat(h-H) # store actually eta
    
    param['output_i'] += 1
    
def output_nc_fin():
    """ Finalise the output netCDF4 file."""
    
    for ncfile in ncfiles:
        ncfile['file'].close()
    
    output_txt('Output written in '+param['runfolder']+'.')

## STORE INFO in TXT FILE
def readable_secs(secs):
    """ Returns a human readable string representing seconds in terms of days, hours, minutes, seconds. """
    
    days = np.floor(secs/3600./24.)
    hours = np.floor((secs/3600.) % 24)
    minutes = np.floor((secs/60.) % 60)
    seconds = np.floor(secs%3600%60)

    if days > 0:
        return ("%id, %ih" % (days,hours))
    elif hours > 0:
        return ("%ih, %imin" % (hours,minutes))
    elif minutes > 0:
        return ("%imin, %is" % (minutes,seconds))
    else:
        return ("%.2fs" % secs)

def duration_est(tic):
    """ Saves an estimate for the total time the model integration will take in the output txt file. """
    if param['output']:
        time_togo = (tictoc.time()-tic) / (i+1) * param['Nt']
        str1 = 'Model integration will take approximately '+readable_secs(time_togo)+', '
        str2 = 'and is hopefully done on '+tictoc.asctime(tictoc.localtime(tic + time_togo))
        output_txt(str1+str2)        
    
def output_txt_ini():
    """ Initialise the output txt file for information about the run."""
    if param['output']:
        param['output_txtfile'] = open(param['output_runpath']+'/info.txt','w')
        s = ('Shallow water model run %i initialised on ' % param['run_id'])+tictoc.asctime()+'\n'
        param['output_txtfile'].write(s)
        
def output_scripts():
    """Save all model scripts into a zip file."""
    if param['output']:
        zf = zipfile.ZipFile(param['output_runpath']+'/scripts.zip','w')
        all_scripts = glob.glob('swm_*.py')
        [zf.write(script) for script in all_scripts]
        zf.close()
        output_txt('All model scripts stored in a zipped file.')
        
def output_txt(s,end='\n'):
    """ Write into the output txt file."""
    if param['output']:
        param['output_txtfile'].write(s+end)
        param['output_txtfile'].flush()

def output_txt_fin():
    """ Finalise the output txt file."""
    if param['output']:
        param['output_txtfile'].close()

## STORE PARAMETERS
def output_param():
    """ Stores the param dictionary in a .npy file """
    if param['output']:
        # filter out 'output_txtfile' as this is a unsaveable textwrapper
        dict_tmp = {key:param[key] for key in param.keys() if key != 'output_txtfile'}
        np.save(param['output_runpath']+'/param.npy',dict_tmp)
        output_txt('Param dictionary stored.\n')