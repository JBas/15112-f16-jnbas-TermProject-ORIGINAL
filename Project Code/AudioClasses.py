import os, sys
from aubio import source, pitch
import pyaudio, math, struct
import numpy as np
import wave


# manages audio from audio files

class AudioFile(object):
	downsample = 1
	win_s = 4096 // downsample # fft size
	hop_s = 512 // downsample # hop size

	# note frequencies
	notes = {
		"rest": 0.0,
		"C1": 32.70,	"C2": 65.41,	"C3": 130.8,	"C4": 261.6,	"C5": 523.3,
		"C#1": 34.65,	"C#2": 69.30,	"C#3": 138.6,	"C#4": 277.2,	"C#5": 554.4,
		"D1": 36.71,	"D2": 73.42,	"D3": 146.8,	"D4": 293.7,	"D5": 587.3,
		"Eb1": 38.89,	"Eb2": 77.78,	"Eb3": 155.6,	"Eb4": 311.1,	"Eb5": 622.3,
		"E1": 41.20,	"E2": 82.41,	"E3": 164.8,	"E4": 329.6,	"E5": 659.3,
		"F1": 43.65,	"F2": 87.31,	"F3": 174.6,	"F4": 349.2,	"F5": 698.5,
		"F#1": 46.25,	"F#2": 92.50,	"F#3": 185.0,	"F#4": 370.0,	"F#5": 740.0,
		"G1": 49.00,	"G2": 98.00,	"G3": 196.0,	"G4": 392.0,	"G5": 784.0,
		"G#1": 51.91,	"G#2": 103.8,	"G#3": 207.7,	"G#4": 415.3,	"G#5": 830.6,
		"A1": 55.00,	"A2": 110.0,	"A3": 220.0,	"A4": 440.0,	"A5": 880.0,
		"Bb1": 58.27,	"Bb2": 116.5,	"Bb3": 233.1,	"Bb4": 466.2,	"Bb5": 932.3,
		"B1": 61.74,	"B2": 123.5,	"B3": 246.9,	"B4": 493.9,	"B5": 987.8	
	}

	# modified from: https://goo.gl/gDjOMB
	def __init__(self, filePath, sampleRate = None):
		self.filePath = filePath
		
		if (sampleRate != None):
			self.sampleRate = sampleRate
		else:
			self.sampleRate = 44100 // AudioFile.downsample

	def __repr__(self):
		return "<%s> : <%d KB>" % (self.filePath, self.fileSize)

	def detectAudioFreq(self, STATE = None):
		s = source(self.filePath, self.sampleRate, AudioFile.hop_s)
		samplerate = self.sampleRate
		samplerate = s.samplerate


		tolerance = 0.8

		global pitch # references imported pitch method (?)


		pitch_o = pitch("default", AudioFile.win_s, AudioFile.hop_s, samplerate)
		pitch_o.set_unit("freq")
		pitch_o.set_tolerance(tolerance)

		pitches = []
		confidences = []

		# total number of frames read
		total_frames = 0
		sumOfPitches = 0
		while True:
			samples, read = s()
			pitch = pitch_o(samples)[0]
			pitch = int(round(pitch))

			confidence = pitch_o.get_confidence()

			if (confidence < 0.5):
				pitch = 0

			pitches += [pitch]
			confidences += [confidence]
			total_frames += read

			sumOfPitches += pitch

			if read < AudioFile.hop_s:
				break

		self.pitches = pitches
		self.meanPitch = sumOfPitches / len(pitches)

		if (STATE == "AVERAGE"):
			return self.meanPitch
		else:
			return pitches

	def goThroughFreq(self):
		notesList = []
		for pitch in self.pitches:
			if (int(pitch) == 0):
				if len(notesList) == 0:
					notesList += ["rest"]
				elif (notesList[-1] != "rest"):
					notesList += ["rest"]
				continue
			for note in AudioFile.notes:
				if (pitch - pitch*0.005 <= AudioFile.notes[note] <= pitch + pitch*0.005):
					if (note != notesList[-1]):
						notesList += [note]
						break
		self.notesList = notesList
		return notesList

	@staticmethod
	# modified from: https://goo.gl/MNeYJy
	def playSong(notes):
		music = []
		for note in notes:
			if note == "rest":
				continue
			music.append(AudioFile.notes[note])
		print(music)

		def PLAY(music):
			def play_tone(frequency, amplitude, duration, fs, stream):
				N = int(fs / frequency)
				T = int(frequency * duration)  # repeat for T cycles
				dt = 1.0 / fs
				# 1 cycle
				tone = (amplitude * math.sin(2 * math.pi * frequency * n * dt)
						for n in xrange(N))

				# todo: get the format from the stream; this assumes Float32
				data = ''.join(struct.pack('f', samp) for samp in tone)
				for n in xrange(T):
					stream.write(data)

			fs = 48000
			p = pyaudio.PyAudio()
			stream = p.open(
				format=pyaudio.paFloat32,
				channels=2,
				rate=fs,
				output=True)

			for tone in music:
				try:
					play_tone(tone, 0.5, 0.75, fs, stream)

				except KeyboardInterrupt:
					sys.exit()

			stream.close()
			p.terminate()

		PLAY(music)





# manages live audio
# cannabalized from https://goo.gl/2PrmTH
# Read from Mic Input and find the freq's
class LiveAudio():
	chunk = 2048

	# use a Blackman window
	window = np.blackman(chunk)
	# open stream
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100

	@staticmethod
	def prepareStream():
		LiveAudio.p = pyaudio.PyAudio()
		LiveAudio.stream = LiveAudio.p.open(format = LiveAudio.FORMAT,
						channels = LiveAudio.CHANNELS,
						rate = LiveAudio.RATE,
						input = True,
						frames_per_buffer = LiveAudio.chunk)
	@staticmethod
	def AnalyzeStream():
		data = LiveAudio.stream.read(LiveAudio.chunk)
		# unpack the data and times by the hamming window
		indata = np.array(wave.struct.unpack("%dh"%(LiveAudio.chunk), data))*LiveAudio.window
		# Take the fft and square each value
		fftData=abs(np.fft.rfft(indata))**2
		# find the maximum
		which = fftData[1:].argmax() + 1
		# use quadratic interpolation around the max
		if which != len(fftData)-1:
			y0,y1,y2 = np.log(fftData[which-1:which+2:])
			x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
			# find the frequency and output it
			thefreq = (which+x1)*LiveAudio.RATE/LiveAudio.chunk
			print("The freq is %f Hz." % (thefreq))
		else:
			thefreq = which*LiveAudio.RATE/chunk
			print("The freq is %f Hz." % (thefreq))
		return thefreq

	@staticmethod
	def closeStream():
		LiveAudio.stream.close()
		LiveAudio.p.terminate


# mananges the visualness of the audio
class sheetMusic(object):
	@staticmethod
	def DEFINE_VARIABLES(data):
		sheetMusic.B5 = [(2*data.height - 5*sheetMusic.staffWidth) // 4, 2]
		sheetMusic.A5 = [(2*data.height - 4*sheetMusic.staffWidth) // 4, 2]
		sheetMusic.G5 = [(2*data.height - 3*sheetMusic.staffWidth) // 4, 2]
		sheetMusic.F5 = [(data.height - sheetMusic.staffWidth) // 2, 2]			# line F
		sheetMusic.D5 = [(2*data.height - sheetMusic.staffWidth) // 4, 2]		# line D
		sheetMusic.B4 = [data.height // 2, 2]									# line B
		sheetMusic.G4 = [(2*data.height + sheetMusic.staffWidth) // 4, 2]		# line G
		sheetMusic.E4 = [(data.height + sheetMusic.staffWidth) // 2, 2]			# line E
		sheetMusic.C4 = [(2*data.height + 3*sheetMusic.staffWidth) // 4, 2]

		sheetMusic.E5 = [(sheetMusic.F5[0] + sheetMusic.D5[0]) // 2]				# space E
		sheetMusic.C5 = [(sheetMusic.D5[0] + sheetMusic.B4[0]) // 2]				# space C
		sheetMusic.A4 = [(sheetMusic.B4[0] + sheetMusic.G4[0]) // 2]				# space A
		sheetMusic.F4 = [(sheetMusic.G4[0] + sheetMusic.E4[0]) // 2]				# space F
		sheetMusic.D4 = [(sheetMusic.E4[0] + sheetMusic.C4[0]) // 2]
		

		sheetMusic.notesX = data.width // 2


	def __init__(self, title = "[Composition1]", musicList = [], timeSig = [4]):
		self.title = title
		self.musicList = musicList
		self.timeSig = timeSig

	def __getitem__(self, index):
		return self.musicList[index]

	def __len__(self):
		return len(self.musicList)

	def __repr__(self):
		return "Creating Sheet Music for %s...!" % self.musicList

	def add(self, note):
		self.musicList.append(note)
	def delete(self):
		self.musicList.pop()

	def drawTitle(self, canvas, data):
		canvas.create_text(data.width // 2, 2*data.offset, text = self.title, font = "Arial 24")
		pass

	def drawNotesFromMusicList(self, canvas, data):
		if (self.musicList == []):
			return
		else:
			for i in range(len(self.musicList)):
				sheetMusic.drawNote(canvas, data, self.musicList[i], i+1)
			return


	@staticmethod
	def drawNote(canvas, data, note, i):
		data.buff = 50
		cx = sheetMusic.notesX + data.buff*i
		if (note == "B5") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.B5[0], image = data.whole_note)
		elif (note == "Bb5") and (data.width > cx > 0):
			canvas.create_image(cx - 0.50*data.buff, sheetMusic.B5[0], image = data.flat_note)
			canvas.create_image(cx, sheetMusic.B5[0], image = data.whole_note)
		elif (note == "A5") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.A5[0], image = data.whole_note)
		elif (note == "G5") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.G5[0], image = data.whole_note)
		elif (note == "G#5") and (data.width > cx > 0):
			canvas.create_text(cx - 0.50*data.buff, sheetMusic.G5[0], text = "#", font = "Arial 32 italic bold")
			canvas.create_image(cx, sheetMusic.G5[0], image = data.whole_note)
		elif (note == "F5") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.F5[0], image = data.whole_note)
		elif (note == "F#5") and (data.width > cx > 0):
			canvas.create_text(cx - 0.50*data.buff, sheetMusic.F5[0], text = "#", font = "Arial 32 italic bold")
			canvas.create_image(cx, sheetMusic.F5[0], image = data.whole_note)
		elif (note == "E5") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.E5[0], image = data.whole_note)
		elif (note == "Eb5") and (data.width > cx > 0):
			canvas.create_image(cx - 0.50*data.buff, sheetMusic.E5[0], image = data.flat_note)
			canvas.create_image(cx, sheetMusic.E5[0], image = data.whole_note)
		elif (note == "D5") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.D5[0], image = data.whole_note)
		elif (note == "D#5") and (data.width > cx > 0):
			canvas.create_text(cx - 0.50*data.buff, sheetMusic.D5[0], text = "#", font = "Arial 32 italic bold")
			canvas.create_image(cx, sheetMusic.D5[0], image = data.whole_note)
		elif (note == "C5") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.C5[0], image = data.whole_note)
		elif (note == "C#5") and (data.width > cx > 0):
			canvas.create_text(cx - 0.50*data.buff, sheetMusic.C5[0], text = "#", font = "Arial 32 italic bold")
			canvas.create_image(cx, sheetMusic.C5[0], image = data.whole_note)
		elif (note == "B4") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.B4[0], image = data.whole_note)
		elif (note == "Bb4") and (data.width > cx > 0):
			canvas.create_image(cx - 0.50*data.buff, sheetMusic.B4[0], image = data.flat_note)
			canvas.create_image(cx, sheetMusic.B4[0], image = data.whole_note)
		elif (note == "A4") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.A4[0], image = data.whole_note)
			#canvas.create_oval(cx - 3*data.noteR//2, sheetMusic.A4[0] - data.noteR,
			#	cx + 3*data.noteR//2, sheetMusic.A4[0] + data.noteR, fill = "red")
		elif (note == "G4") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.G4[0], image = data.whole_note)
		elif (note == "G#4") and (data.width > cx > 0):
			canvas.create_text(cx - 0.50*data.buff, sheetMusic.G4[0], text = "#", font = "Arial 32 italic bold")
			canvas.create_image(cx, sheetMusic.G4[0], image = data.whole_note)
			#canvas.create_oval(cx - 3*data.noteR//2, sheetMusic.G4[0] - data.noteR,
			#	cx + 3*data.noteR//2, sheetMusic.G4[0] + data.noteR, fill = "red")
		elif (note == "F4") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.F4[0], image = data.whole_note)
		elif (note == "F#4") and (data.width > cx > 0):
			canvas.create_text(cx - 0.50*data.buff, sheetMusic.F4[0], text = "#", font = "Arial 32 italic bold")
			canvas.create_image(cx, sheetMusic.F4[0], image = data.whole_note)
			#canvas.create_oval(cx - 3*data.noteR//2, sheetMusic.F4[0] - data.noteR,
			#	cx + 3*data.noteR//2, sheetMusic.F4[0] + data.noteR, fill = "red")
		elif (note == "E4") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.E4[0], image = data.whole_note)
		elif (note == "Eb4") and (data.width > cx > 0):
			canvas.create_image(cx - 0.50*data.buff, sheetMusic.E4[0], image = data.flat_note)
			canvas.create_image(cx, sheetMusic.E4[0], image = data.whole_note)
		elif (note == "C4") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.C4[0], image = data.whole_note)
		elif (note == "C#4") and (data.width > cx > 0):
			canvas.create_text(cx - 0.50*data.buff, sheetMusic.C4[0], text = "#", font = "Arial 32 italic bold")
			canvas.create_image(cx, sheetMusic.C4[0], image = data.whole_note)
		elif (note == "D4") and (data.width > cx > 0):
			canvas.create_image(cx, sheetMusic.D4[0], image = data.whole_note)
		elif (note == "rest") and (data.width > cx > 0):
			canvas.create_rectangle(cx - data.noteR, sheetMusic.B4[0],
				cx + data.noteR, data.height // 2 - data.noteR, fill = "red")
		else:
			canvas.create_oval(cx - data.noteR, sheetMusic.B4[0],
				cx + data.noteR, data.height // 2 - data.noteR, fill = "blue")
		pass


	@staticmethod
	def drawStaff_LEARNING(canvas, data):
		def drawLines(canvas, data, margin = 0):
			canvas.create_line(0 - data.offset, sheetMusic.F5[0] + margin, data.width + data.offset,
				sheetMusic.F5[0] + margin, width = sheetMusic.F5[1]) #, activefill = "blue", fill = "black"
			canvas.create_line(0 - data.offset, sheetMusic.D5[0] + margin, data.width + data.offset,
				sheetMusic.D5[0] + margin, width = sheetMusic.D5[1]) #, activefill = "blue", fill = "black"
			canvas.create_line(0 - data.offset, sheetMusic.B4[0] + margin, data.width + data.offset,
				sheetMusic.B4[0] + margin, width = sheetMusic.B4[1]) #, activefill = "blue", fill = "black"
			canvas.create_line(0 - data.offset, sheetMusic.G4[0] + margin, data.width + data.offset,
				sheetMusic.G4[0] + margin, width = sheetMusic.G4[1]) #, activefill = "blue", fill = "black"
			canvas.create_line(0 - data.offset, sheetMusic.E4[0] + margin, data.width + data.offset,
				sheetMusic.E4[0] + margin, width = sheetMusic.E4[1]) #, activefill = "blue", fill = "black"


		# draws "cursor"
		canvas.create_rectangle((0 - data.offset), (data.height - sheetMusic.staffWidth) // 2,
			(data.width + data.offset), (data.height + sheetMusic.staffWidth) // 2,
			width = 0, fill = "white")
		drawLines(canvas, data)

		if data.MODE == "LEARNING":
			canvas.create_line(data.width // 2, (data.height - sheetMusic.staffWidth) // 2, data.width // 2, (data.height + sheetMusic.staffWidth) // 2, width = 5, fill = "red")

		# TREBLE CLEF REPRESENTATION!
		canvas.create_image(30, data.height // 2, image = data.clef)
	pass