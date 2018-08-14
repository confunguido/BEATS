#!/usr/local/bin/python3
##!/usr/bin/python3
#======================================================================
# Author: Guido Espana
# Date: 24/07/2018
# Normalizes a timeseries to tones within a specific key
#======================================================================
import sys
import os
import re
import math
import numpy as np
import pandas as pd
import argparse
import music21 as mus
import matplotlib as mpl
import matplotlib.pyplot as plt
#======================================================================
# Classes
#======================================================================
class ts2music:
    def __init__(self,music_key,minor,ts,col_name):
        self.lowkey = 27
        self.midkey = 39
        self.highkey = 63
        self.maxkeys = 75
        self.minor = minor
        self.key_scale = music_key
        self.fundamental_notes = {            
            'C': 4,'C#':5, 'D-':5,
            'D': 6,'D#':7, 'E-':7,
            'E': 8,'E#':9, 'F-':8,
            'F': 9,'F#':10, 'G-':10,
            'G': 11,'G#':12, 'A-':12,
            'A': 13,'A#':14, 'B-':14,
            'B': 15,'B#':16, 'C-':16
        }
        
        self.timeseries =  ts
        self.col = col_name
        self.fundamental = self.fundamental_notes[self.key_scale]
        self.key_notes = {
            4:'C', 5:'C#',6:'D',7:'D#',
            8:'E',9:'F',10:'F#',11:'G',12:'G#',
            13:'A',14:'A#',15:'B'
        }
        if not minor:
            self.scale = np.array([0,2,4,5,7,9,11])
        else:
            self.scale = np.array([0,2,3,5,7,8,10])
            
    def get_n_piano_key(self,f):
        return(round(12*math.log2(f/440) + 49))

    def get_freq_from_key(self,n):
        return(2**((n-49)/12)*440)

    def find_semitones_from_note(self,f1,f2):
        n1 = self.get_n_piano_key(f1)
        n2 = self.get_n_piano_key(f2)
        dn = math.fmod(n2 - n1,12)
        if dn < 0:
            return(round(dn+12))
        else:
            return(round(dn))    
    
    def adjust_freq_to_key_scale(self,f):
        n = self.get_n_piano_key(f)
        note = self.adjust_key_to_scale(n)
        return(note)
    
    def adjust_key_to_scale(self,n):
        if n < 1: return('Rest')
        #if n < 4: n = 4
        pianokeys = np.array([])        
        for i in range(7):
            pianokeys = np.append(pianokeys,self.fundamental + self.scale + 12*i)
        #print(pianokeys)
        dmin = pianokeys[np.argmin(np.abs(pianokeys - n))]
        octave = math.floor(dmin/ 12) + 1
        note = dmin % 12
        if note < 4 :
            note += 12
            octave-=1
        notestr = self.key_notes[note]
        return('%s%d'%(notestr,octave))

    def add_notes_to_timeseries(self):
        self.timeseries['Notes'] = np.repeat('',self.timeseries.shape[0])
        maxcases = self.timeseries[self.col].max()
        cases_qnt = self.timeseries[self.col][self.timeseries[self.col] > 0].quantile([.05,.95])
        lowcases = cases_qnt[0.05]
        highcases = cases_qnt[0.95]
        caseskeys = np.repeat(0,self.timeseries.shape[0])
        
        # low numbers of cases
        ind = np.where((self.timeseries[self.col] > 0) & (self.timeseries[self.col] <= lowcases))[0]
        caseskeys[ind] = (self.timeseries[self.col][ind] / lowcases) * (self.midkey - self.lowkey) + self.lowkey

        # mid numbers of cases
        ind = np.where((self.timeseries[self.col] > 0) & (self.timeseries[self.col] > lowcases) &
                       (self.timeseries[self.col] <= highcases))[0]

        caseskeys[ind] = np.floor(
            ((self.timeseries[self.col][ind] - lowcases) / (highcases - lowcases)) *
            (self.highkey - self.midkey) + self.midkey
        )

        # high numbers of cases
        ind = np.where((self.timeseries[self.col] > 0) & (self.timeseries[self.col] > highcases))[0]
        caseskeys[ind] = np.floor(
            ((self.timeseries[self.col][ind] - highcases) / (maxcases - highcases)) *
            (self.maxkeys - self.highkey) + self.highkey
        )
        
        self.timeseries['Notes'] = np.array([self.adjust_key_to_scale(n) for n in caseskeys])
        self.timeseries['Key'] = np.array(caseskeys).astype(int)
    
    def export_timeseries_notation(self,outfile):
        self.timeseries.to_csv(outfile,index=False)
    
    def get_stream_part_from_timeseries(self):
        part_tmp = mus.stream.Part(id=str(self.col))
        if self.minor:
            part_tmp.append(mus.key.Key(self.key_scale,'minor'))
        else:
            part_tmp.append(mus.key.Key(self.key_scale))
    
        notes = list(self.timeseries['Notes'])
        for n in notes:
            if n != 'Rest':
                part_tmp.append(mus.note.Note(n,type="quarter"))
            else:
                part_tmp.append(mus.note.Rest(type="quarter"))
        return(part_tmp)

#======================================================================
# Functions
#======================================================================
def standarize_timeseries(list_of_ts, names_in, unique_time):
    # Unique and sorted time (Year,Week)
    time_dict = dict()
    for n in unique_time:
        time_dict[n[0] + n[1]/52.0] = n
    sk = sorted(time_dict)
    sorted_year = [time_dict[k][0] for k in sk]
    sorted_weeks = [time_dict[k][1] for k in sk]
    std_timeseries = dict(zip(names_in,[0 for n in names_in]))
    std_timeseries['Year'] = sorted_year
    std_timeseries['Week'] = sorted_weeks
    
    std_ts = pd.DataFrame(std_timeseries)

    for nn in range(len(sorted_year)):
        for ff in range(len(list_of_ts)):
            df_tmp = list_of_ts[ff]
            df = df_tmp[(df_tmp['Year'] == sorted_year[nn]) & (df_tmp['Week']==sorted_weeks[nn])]
            if not df.empty:
                std_ts[names_in[ff]][nn] = df['Cases']

    return(std_ts)

#======================================================================
# Functions
#======================================================================
def plot_timeseries(df,day,names_in,dir_figs):
    fig, axarr = plt.subplots(len(names_in), sharex=True)
    time_ts = df['Year'] + df['Week'] / 52.0
    for x in range(len(axarr)):
        maxcases = df[names_in[x]].max()
        axarr[x].plot(time_ts, df[names_in[x]],linestyle = '-',color = 'black', alpha= 1.0, linewidth = 2)
        axarr[x].plot([time_ts[day],time_ts[day]],[0,maxcases],color='gray')
        axarr[x].set_ylabel(names_in[x])
    plt.savefig('%s/BEATS_tmp_%05d.png' % (dir_figs,day),format='png')
    plt.close(fig)


#======================================================================
# Main routine
#======================================================================
def main():
    parser = argparse.ArgumentParser(
            description='Specify frequency, scale, tempo, and tonality' )
    parser.add_argument("-f", type = str,help = "Select the file with the timeseries", required = True)
    parser.add_argument("-s", type = str,help = "Scale in international notation", default  = 'C')
    parser.add_argument("-t", type = int,help = "Tempo [default 180]", default = 180)
    parser.add_argument("--minor", help = "Enable minor scale", default = False, action="store_true")

    args = parser.parse_args()
    tsfile = args.f
    scale = args.s
    tempo = math.floor(args.t / 60) * 60
    minor = args.minor
    
    score_stream = mus.stream.Score(id='mainScore')
    score_stream.insert(0, mus.metadata.Metadata())
    score_stream.metadata.title = 'Epidemics'
    score_stream.metadata.composer = 'B.E.A.T.S'
    filenames = pd.read_csv(tsfile,sep='\s*,\s*', engine='python')
    timeseries_list = list()
    names_list = list(filenames['Name'])
    time_tuple = list()
    midi_programs = list(filenames['MidiInstrument']) #[41,1,74]
    for ff in range(filenames.shape[0]):
        ts_tmp = pd.read_csv(filenames['File'][ff],sep='\s*,\s*',engine='python')
        time_tuple.extend([(ts_tmp['Year'][n],ts_tmp['Week'][n]) for n in range(ts_tmp.shape[0])])
        ts_tmp['Year.Week'] = ts_tmp['Year']+ts_tmp['Week']/52.0
        #names_list.append(filenames['Name'][ff])
        timeseries_list.append(ts_tmp)

    std_case_data = standarize_timeseries(timeseries_list,names_list,set(time_tuple))
    for n in range(len(names_list)):
        creator = ts2music(scale,minor,std_case_data,names_list[n])
        creator.add_notes_to_timeseries()        
        ptmp = creator.get_stream_part_from_timeseries()        
        ptmp.insert(0, mus.tempo.MetronomeMark(number = tempo, referent = mus.note.Note(type='quarter')))
        ptmp.partName = names_list[n]
        ptmp.insert(0,mus.instrument.Clarinet())
        ptmp.getElementsByClass('Instrument')[0].midiProgram = midi_programs[n]
        ptmp.getElementsByClass('Instrument')[0].instrumentName =  names_list[n]
        ptmp.getElementsByClass('Instrument')[0].instrumentAbbreviation =  names_list[n]

        score_stream.insert(0,ptmp)        
        print(ptmp.partName)

    score_stream.makeNotation()
    fp = score_stream.write('midi',fp='tmp.mid')
    score_stream.show('midi')
    os.system('fluidsynth -F tmp.wav resources/MuseScore_General.sf2 tmp.mid -g 2')
    #score_stream.show()
    
    # Now I need to just plot a figure with N rows and add a vertical bar
    # for each week
    outdir = './output'
    outfigs = outdir + '/figures'
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    if not os.path.isdir(outfigs):
        os.mkdir(outfigs)
    for d in range(std_case_data.shape[0]):
        plot_timeseries(std_case_data,d,names_list,outfigs)
        
    # Create a video with the incidence curves and the music
    video_rate = tempo / 60.0
    os.system('ffmpeg -r %d -i output/figures/BEATS_tmp_%%05d.png -i tmp.wav -c:v libx264 -c:a aac -shortest -pix_fmt yuv420p output.mp4 -y' % (video_rate))

#======================================================================
# Call main 
#======================================================================
if __name__ == '__main__':
    main()


    #outbase = os.path.splitext(os.path.basename(tsfile))[0]
    #creator.export_timeseries_notation('data/output/'+ outbase +'_notation.csv')
