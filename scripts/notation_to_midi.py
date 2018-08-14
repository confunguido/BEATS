#!/usr/bin/python
#======================================================================
# Author: Guido Espana
# Date: 24/07/2018
# Writes a timeseries of notes to a music score
#======================================================================
import numpy as np
import pandas as pd
import sys
import os
import re
import math
import argparse
import mingus.containers
from mingus.containers import Bar
from mingus.containers import Track
from mingus.containers import Composition
from mingus.containers.instrument import Instrument, Piano, Guitar, MidiInstrument
import mingus.extra.lilypond as LilyPond
from mingus.midi import midi_file_out

#======================================================================
# Classes
#======================================================================
class music_converter:
    def __init__(self,music_key,major,tempo, tsfile):
        self.key = music_key
        self.tempo = tempo
        self.timeseries =  pd.read_csv(tsfile,sep='\s*,\s*', engine='python')        
        self.composition = Composition()
        self.composition.set_author('Guido','confunguido@gmail.com')
        self.composition.set_title('Epidemics')
        
    def write_mingus(self,outfile):
        notes = list(self.timeseries['Notes'])
        t = Track()
        for n in range(len(notes)):
            if n % 4 == 0:
                b = Bar(self.key,(4,4))
            if notes[n] !='Z':
                b + notes[n]
            else:
                b + None
            if (n+1) % 4 == 0:
                t + b
        self.composition + t
        self.track = t
        lily_composition = LilyPond.from_Composition(self.composition)
        print lily_composition
        LilyPond.to_pdf(lily_composition,outfile)
        
    def write_midi(self,outfile):        
        midi_file_out.write_Composition(outfile,self.composition,bpm=self.tempo)
        
#======================================================================
# Main routine
#======================================================================
def main():
    parser = argparse.ArgumentParser(
            description='Specify frequency, scale, tempo, and tonality' )
    parser.add_argument("-f", type = str,help = "Select the file with the timeseries", required = True)
    parser.add_argument("-o", type = str,help = "Select the output name", default = "Test")
    parser.add_argument("-s", type = str,help = "Scale in international notation", default  = 'C')
    parser.add_argument("-t", type = int,help = "Tempo [default 190]", default = 190)
    parser.add_argument("--min", help = "Enable minor scale", default = False, action="store_true")

    args = parser.parse_args()
    tsfile = args.f
    outfile = args.o
    scale = args.s
    tempo = args.t
    major = not args.min
        
    mwriter = music_converter(scale,major,tempo,tsfile)
    mwriter.write_mingus(outfile)
    mwriter.write_midi(outfile + '.mid')
#======================================================================
# Call main 
#======================================================================
if __name__ == '__main__':
    main()
