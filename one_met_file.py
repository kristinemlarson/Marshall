import numpy as np
import os 
import subprocess
import matplotlib.pyplot as plt
import sys

import gnssrefl.gps as g
import gnssrefl.kelly as kelly
import gnssrefl.sd_libs as sd

def met_unavco(station,year,doy):
    """
    """
    y, month, day, cyyyy,cdoy, YMD = g.ydoy2useful(year,doy)
    xdir = 'https://data.earthscope.org/archive/gnss/rinex/met/'  + cyyyy + '/' + cdoy + '/'
    f = station + cdoy + '0.' + cyyyy[2:4] + 'm'
    fz = f + '.Z'
    url = xdir   + fz 
    #print(url)
    foundit,file_name = kelly.the_kelly_simple_way(url,fz)
    if foundit:
        subprocess.call(['uncompress', fz])


    return foundit, f 

def one_met_file(station, year,doy,localdir):
    """

    Reads and collates the met data?  if the met file is 
    not on disk, it tries to download it from unavco

    Lazy - it assumes the pressure and temperature data will 
    always be in the same columns.  What could go wrong?

    Parameters
    ----------
    station : str
        four char station name
    year : int
        calendar year
    doy : int
        day of year 
    localdir : str
        where to find the met data


    Returns
    -------
    mval : numpy array
        modified julian date
    temperature : numpy array of floats
        deg C
    pressure : numpy array of floats
        I think it is negative ? because ...
    """

    mval = []
    pressure = []
    temperature = []
    rain = []
    #print(found,fname)

    d = doy
    if True:
        y, month, day, cyyyy,cdoy, YMD = g.ydoy2useful(year,d)
        cyy = cyyyy[2:4]
        f=  station + cdoy +  '0.' + cyy + 'm'
        localfile = localdir + f

        if not os.path.isfile(localfile):
            found,fname = met_unavco(station,year,doy)
            if found:
                subprocess.call(['mv', fname, localdir])

        if not os.path.isfile(localfile):
            print('still have not found it')
        else:
        # get number of header lines
            numlines,nobs,pindex,tindex,rindex = nlines(localfile)
            #print(nobs,pindex, tindex, rindex)
            #print('Lines in the header ', numlines, nobs)
            try : 
                a = np.loadtxt(localfile,skiprows=numlines,comments='%')
            except:
                print('some kind of problem. will try to repair', localfile)
                badlines(localfile,numlines)
                try: 
                    if os.path.isfile(localfile):
                        a = np.loadtxt(localfile,skiprows=numlines,comments='%')
                except:
                    print('failed again')
                    a = []

            nr = len(a)
            if (nr >0):
                for i in range(0,len(a)):
                    mjdi, mjdf = g.mjd(a[i,0]+2000, a[i,1], a[i,2],a[i,3], a[i,4],a[i,5])
                    mval.append(mjdi + mjdf)
                    if pindex > 0:
                        pressure.append(float(a[i,5+pindex]))
                    if tindex > 0:
                        temperature.append(float(a[i,5+tindex]))
                    if rindex > 0:
                        rain.append(float(a[i,5+rindex]))

    mval = np.asarray(mval)
    temperature = np.asarray(temperature)
    pressure = np.asarray(pressure)
    rain = np.asarray(rain)

    #print('Number of met observations ', len(mval))
    return mval, temperature, pressure, rain

def badlines(filename,numlines):
    """
    looks for 999 values and writes a new file without those.

    filename : str
        name of the met file
    numlines : int
        number of lines in the header

    """
    i = 1
    newfile = filename + '.txt'
    fout = open(newfile, 'w+')
    with open(filename) as file:
        for line in file:
            #print(i,line)
            if (i > numlines): # not in the header
                if '999' in line:
                    line = line.replace('-9999.9','   -9.9')
                    #print('newline ', line)
            fout.write(line)
            i = i + 1

    fout.close()
    subprocess.call(['rm', filename])
    #print('New file created for ', filename)
    subprocess.call(['mv', newfile, filename])

def nlines(filename):
    """
    return number of header lines

    return index of the obs def line
    """
    rindex = 0; tindex = 0; pindex = 0
    i = 1
    with open(filename) as file:
        for line in file:
            if 'TYPES OF OBSERV' in line:
                #print(line)
                values = line[0:60].split()
                nv = int(values[0])
                for j in range(nv):
                    #print(j+1, values[j+1])
                    if values[j+1] == 'PR':
                        pindex = j+1
                    if values[j+1] == 'TD':
                        tindex = j+1
                    if values[j+1] == 'RI': # rain increment
                        rindex = j+1

            if 'END' in line.rstrip():
                break
            i = i + 1

    numberLines = i
    return numberLines, nv, pindex, tindex, rindex

def rainfig(year, mval, rain):
    """
    """
    fig=plt.figure()
#     dtime = sd.mjd_to_obstimes(d+0.5)
    plt.bar(sd.mjd_to_obstimes(mval),rain,width=1.5 )
    plt.title('using RINEX sensor for p041/be aware of contamination by snow!')
    plt.ylabel('cumulative precip (mm)')
    plt.grid()
    m1 = sd.mjd_to_obstimes(mval[0]) ; m2 = sd.mjd_to_obstimes(mval[-1])
    plt.xlim((m1, m2))
    fig.autofmt_xdate()
    plt.show()

def main():
    station = 'p041'
    year = 2014
    dec31 = g.dec31(year)

    localdir = 'temperature/' + station + '/' + str(year) + '/'
    if not os.path.isdir(localdir):
        subprocess.call(['mkdir', '-p', localdir])

    print('Cumulative precipitation (mm) \n')
    keep_mjd = []
    keep_precip = []
    for doy in range(1,dec31+1):
    
        mval, temp, pressure, rain = one_met_file(station, year, doy, localdir)
        if len(rain) > 0:
            # remove the -9.9 points
            ij = rain > -1
            rain = rain[ij]
            mval = mval[ij]
            # kluge ?? 
            yy,mm,dd, cyyyy, cdoy, YMD = g.ydoy2useful(year,doy)
            # cause the sensor is goofy - 
            if (rain[0] > 100) and (year < 2012):
                rain = rain - rain[0]

            cumprecip = (np.cumsum(rain)[-1])/10

            nogood = False
            if cumprecip < 0:
                nogood = True
                print('Bad dat? ', np.round(cumprecip,2), ' for : ', year, doy, mm, dd)
            elif (cumprecip > 70): # to allow boulder massive rain event on 2023/9/12 and days following
                if year == 2013:
                    nogood = False
                else:
                    print('Bad dat? ', np.round(cumprecip,2), ' for : ', year, doy, mm, dd)
                    nogood = True
            if not nogood:
                print("{0:5.2f} {1:4.0f} {2:3.0f} {3:2.0f} {4:2.0f} ".format(cumprecip, year,doy,mm,dd))
                keep_mjd.append(np.floor(mval[0]))
                keep_precip.append(cumprecip)

    mjd = np.asarray(keep_mjd)
    precip = np.asarray(keep_precip)
    rainfig(year,mjd,precip)


if __name__ == "__main__":
    main()

