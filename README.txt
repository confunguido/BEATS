Plan:
0. Choose a key
1. Standarize timeseries and normalize to frequencies from the chosen key
2. Output the frequencies
3. Choose an instrument
4. Use LilyPond to write the sheet music
5. Use fluidSynth and Mingus to generate the tones with the chosen instrument... look in: https://bspaans.github.io/python-mingus/index.html
6. Generate MIDI/MP3 or other sound file... it would be nice to play everything with the sheet music at the same time

-- 
Now I am using Music21 instead of Mingus, it's much better =D

- Try this to add sound to the video: 
  ffmpeg -i video.avi -i audio.mp3 -codec copy -shortest output.avi
  ffmpeg -i output/figures/BEATS_tmp_%05d.png -i tmp.wav -c:v libx264 -c:a copy -shortest out.mp4

- TO convert to WAV use:
  fluidsynth -ni sound_font.sf2 input.mid -F output.wav -r 44100

