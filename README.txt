#=====================================
# README
#=====================================
BEATS: Basic Epidemic to Audio Transformation Software.

beats.py -f timeseries_files -s scale [C] -o output video [output] -t tempo [180] --minor [optional]

- timeseries_files:
	- Each line contains the names of the files with the epidemic timeseries
	- Each file should be a .csv file with the columns Year,Week,Cases

--minor. If minor is not indicated a major scale is used

#=====================================
# Dependencies
#=====================================

BEATS relies on some python packages and additional audio software.

1. Python packages:
	- Music21
	- Pandas
	- matplotlib
2. Audio/Video software:
	- ffmpeg
	- fluid synth with sound font. Currently, BEATS relies on this sound font to be located in resources/MuseScore_General.sf2
	
#=====================================
# Steps inside BEATS
#=====================================
0. Choose a key
1. Standarize timeseries and normalize to frequencies from the chosen key
2. Output the frequencies
3. Choose an instrument
4. Use Music21 to export to Midi 
5. Convert midi to wav using fluid synth. Soundfont should be downloaded. I'm using MuseScore_General.sf2
  fluidsynth -ni sound_font.sf2 input.mid -F output.wav -r 44100
6. Create a video using ffmpeg
	
  ffmpeg -r <rate> -i output/figures/BEATS_tmp_%05d.png -i tmp.wav -c:v libx264 -c:a aac -shortest -pix_f\
mt yuv420p output.mp4 -y