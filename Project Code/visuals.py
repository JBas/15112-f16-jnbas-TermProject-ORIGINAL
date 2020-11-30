from Tkinter import *
from AudioClasses import AudioFile, LiveAudio, sheetMusic
import os, ast

# taken from class notes
def rgbString(red, green, blue):
	return "#%02x%02x%02x" % (red, green, blue)


def init(data):
	data.prevMODE = "startScreen"
	data.MODE = "startScreen"
	data.offset = 10
	data.rightScroll = False
	data.leftScroll = False

	data.buttonWidth = 150
	data.buttonHeight = data.buttonWidth // 3
	data.playS = 75.0

	data.clef = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/treble_clef.gif")
	data.whole_note = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/whole-note.gif")
	data.background = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/startBackground.gif")
	data.flat_note = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/flat.gif")

	# https://goo.gl/7vNcpi
	data.NORMALbutton = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/normal.gif")
	#https://goo.gl/2YJtp2
	data.LEARNINGbutton = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/learning.gif")
	# https://goo.gl/ZnL1hb
	data.help = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/helpIcon.gif")
	# https://goo.gl/qFnM5q
	data.home = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/homeIcon.gif")
	# https://goo.gl/B10b8H
	data.saveComposition = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/save.gif")
	# https://goo.gl/tvqIdL
	data.openComposition = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/open.gif")
	# https://goo.gl/pB48rh
	data.playButton_NORMAL = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/playButton1.gif")
	data.playButton_LEARNING = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/playButton2.gif")
	#https://goo.gl/6KIYSw
	data.practiceButton = PhotoImage(file="/Users/Joshua/Desktop/Term Project/media/visuals/practice.gif")

	data.music = sheetMusic(title = "My Song", musicList = [])

	pass


def updateMode(data):
	if (data.MODE == "NORMAL"):
		sheetMusic.staffWidth = 200
		data.noteR = 10
		sheetMusic.DEFINE_VARIABLES(data)
		sheetMusic.notesX = 10

		data.staffRow = 0
	elif (data.MODE == "LEARNING"):
		sheetMusic.staffWidth = 100
		data.noteR = 10

		sheetMusic.DEFINE_VARIABLES(data)
		data.audio = AudioFile("/Users/Joshua/Desktop/Term Project/media/sounds/Tuning Note A.wav")
		data.audio.detectAudioFreq()
		data.music = sheetMusic(title = "", musicList = data.audio.goThroughFreq())
		print(data.music)


def checkNotes(note, data):
	LiveAudio.prepareStream()

	while True:
		if note == "rest":
			sheetMusic.notesX -= data.buff
			break
		targetFreq = AudioFile.notes[note]
		freq = LiveAudio.AnalyzeStream()
		print("tgt = %d" % targetFreq)
		if (targetFreq - targetFreq * 0.0005 <= freq <= targetFreq + targetFreq * 0.0005):
			sheetMusic.notesX -= data.buff
			break

	LiveAudio.closeStream()
	return

def saveComposition(data):
	# modified from: https://goo.gl/gCDCyU
	i = 1
	while True:
		if ("MyComposition%d.txt" % i) not in os.listdir("/Users/Joshua/Desktop/Term Project/media/Saved Compositions/"):
			filepath = os.path.join("/Users/Joshua/Desktop/Term Project/media/Saved Compositions/",
				"MyComposition%d.txt" % i)
			break
		i += 1
	file = open("%s" % filepath, "w")
	filename = "%s" % data.music.musicList
	file.write(filename[1:-1])
	file.close()

def openComposition(data):
	filepath = os.path.join("/Users/Joshua/Desktop/Term Project/media/Saved Compositions/",
		"%s" % os.listdir("/Users/Joshua/Desktop/Term Project/media/Saved Compositions/")[-1])
	file = open("%s" % filepath, "r")
	data.music.musicList = list(ast.literal_eval(file.read()))
	file.close()


def mousePressed(event, canvas, data):
	if ((data.width - 4*data.offset - 10 <= event.x <= data.width - 4*data.offset + 10) and 
		(data.height - 4*data.offset - 10 <= event.y <= data.height - 4*data.offset + 10)):
		data.MODE = "helpScreen"
	elif ((data.width - 12*data.offset - 10 <= event.x <= data.width - 12*data.offset + 10) and
		(data.height - 4*data.offset <= event.y <= data.height + 4*data.offset)):
		data.MODE = "startScreen"
		data.prevMODE = "startScreen"
	elif (data.MODE == "startScreen"):
		mousePressedStartScreen(event, data)
	elif (data.MODE == "NORMAL"):
		mousePressed_NORMAL(event, data)
	elif (data.MODE == "LEARNING"):
		mousePressed_LEARNING(event, canvas, data)
	elif (data.MODE == "helpScreen"):
		mousePressed_HELP(event, data)
	pass

def mousePressed_HELP(event, data):
	data.MODE = data.prevMODE


def mousePressed_NORMAL(event, data):
	if ((0 <= event.x <= 2*data.offset) and
		((data.height - 20*data.offset) // 2 <= event.y <= (data.height + 20*data.offset) // 2)):
		sheetMusic.notesX += 20
	elif ((data.width - 2*data.offset <= event.x <= data.width) and
		((data.height - 20*data.offset) // 2 <= event.y <= (data.height + 20*data.offset) // 2)):
		sheetMusic.notesX -= 20

	if ((data.width - 5*data.offset - 25 <= event.x <= data.width - 5*data.offset + 25) and
		(5*data.offset - 25 <= event.y <= 5*data.offset + 25)):
		saveComposition(data)
	elif ((data.width - 5*data.offset - 25 <= event.x <= data.width - 5*data.offset + 25) and
		(15*data.offset - 25 <= event.y <= 15*data.offset + 25)):
		openComposition(data)

	if (sheetMusic.F5[0] - sheetMusic.F5[1] <= event.y <= sheetMusic.F5[0] + sheetMusic.F5[1]):
		data.music.add("F5")
	elif (event.y == sheetMusic.E5[0]):
		data.music.add("E5")
	elif (sheetMusic.D5[0] - sheetMusic.D5[1] <= event.y <= sheetMusic.D5[0] + sheetMusic.D5[1]):
		data.music.add("D5")
	elif (event.y == sheetMusic.C5[0]):
		data.music.add("C5")
	elif (sheetMusic.B4[0] - sheetMusic.B4[1] <= event.y <= sheetMusic.B4[0] + sheetMusic.B4[1]):
		data.music.add("B4")
	elif (event.y == sheetMusic.A4[0]):
		data.music.add("A4")
	elif (sheetMusic.G4[0] - sheetMusic.G4[1] <= event.y <= sheetMusic.G4[0] + sheetMusic.G4[1]):
		data.music.add("G4")
	elif (event.y == sheetMusic.F4[0]):
		data.music.add("F4")
	elif (sheetMusic.E4[0] - sheetMusic.E4[1] <= event.y <= sheetMusic.E4[0] + sheetMusic.E4[1]):
		data.music.add("E4")
	# play button
	elif (5*data.offset - 25 <= event.x <= 5*data.offset + 25) and (5*data.offset - 25 <= event.y <= 5*data.offset + 25):
		AudioFile.playSong(data.music.musicList)
	pass


def mousePressed_LEARNING(event, canvas, data):
	if ((5*data.offset - 25 <= event.x <= 5*data.offset + 25) and
		(15*data.offset - 25 <= event.y <= 15*data.offset + 25)):
		for note in data.music:
			checkNotes(note, data)
			canvas.delete(ALL)
			redrawAll_LEARNING(canvas, data)
			canvas.update() 
	elif ((5*data.offset - 25 <= event.x <= 5*data.offset + 25) and
		(5*data.offset - 25 <= event.y <= 5*data.offset + 25)):
		AudioFile.playSong(data.audio.notesList)
	pass


def mousePressedStartScreen(event, data):
	if ((data.width // 2 - 75 <= event.x <= data.width // 2 + 75) and
		(data.height // 4 - 75 <= event.y <= data.height //4 + 75)):
		data.MODE = "LEARNING"
		data.prevMODE = "LEARNING"
		updateMode(data)
	elif ((data.width // 2 - 75 <= event.x <= data.width // 2 + 75) and
		(data.height * 3 // 4 - 75 <= event.y <= data.height * 3 //4 + 75)):
		data.MODE = "NORMAL"
		data.prevMODE = "NORMAL"
		updateMode(data)

	pass


def mouseMotion(event, canvas, data):
	if (data.MODE == "NORMAL"):
		mouseMotion_NORMAL(event, canvas, data)
	pass


def mouseMotion_NORMAL(event, canvas, data):
	if (event.x >= data.width - 2*data.offset):
		data.rightScroll = True
	elif (event.x <= 2*data.offset):
		data.leftScroll = True
	else:
		data.rightScroll = False
		data.leftScroll = False

	if (sheetMusic.F5[0] - 5 < event.y < sheetMusic.F5[0] + 5):
		sheetMusic.F5[1] = 3
	elif (sheetMusic.D5[0] - 5 < event.y < sheetMusic.D5[0] + 5):
		sheetMusic.D5[1] = 3
	elif (sheetMusic.B4[0] - 5 < event.y < sheetMusic.B4[0] + 5):
		sheetMusic.B4[1] = 3
	elif (sheetMusic.G4[0] - 5 < event.y < sheetMusic.G4[0] + 5):
		sheetMusic.G4[1] = 3
	elif (sheetMusic.E4[0] - 5 < event.y < sheetMusic.E4[0] + 5):
		sheetMusic.E4[1] = 3
	else:
		sheetMusic.F5[1] = 2
		sheetMusic.D5[1] = 2
		sheetMusic.B4[1] = 2
		sheetMusic.G4[1] = 2
		sheetMusic.E4[1] = 2


def keyPressed(event, data):
	if (event.keysym == "B"):
		data.MODE = "startScreen"
	elif (data.MODE == "LEARNING"):
		keyPressed_LEARNING(event, data)
	elif (data.MODE == "NORMAL"):
		keyPressed_NORMAL(event, data)
	pass


def keyPressed_LEARNING(event, data):
	if (event.keysym == "w") and (data.WRONG == True):
		data.WRONG = False
	elif (event.keysym == "w"):
		data.WRONG = True

	pass

def keyPressed_NORMAL(event, data):
	if (event.keysym == "BackSpace"):
		data.music.delete()


def timerFired(data):
	pass



def redrawAllStartScreen(canvas, data):
	backgroundColor = rgbString(142,229,161)
	canvas.create_rectangle(0 - data.offset, 0 - data.offset,
		data.width + data.offset, data.height + data.offset,
		width = 0, fill = backgroundColor)
	canvas.create_image(data.width // 2, data.height // 2,
		image = data.background)
	canvas.create_image(data.width // 2, data.height // 4,
		image = data.LEARNINGbutton)
	canvas.create_image(data.width // 2, data.height * 3 // 4,
		image = data.NORMALbutton)


def redrawAll_LEARNING(canvas, data):
	sheetMusic.drawStaff_LEARNING(canvas, data)
	data.music.drawTitle(canvas, data)
	data.music.drawNotesFromMusicList(canvas, data)
	canvas.create_image(5*data.offset, 5*data.offset, 
		image = data.playButton_LEARNING)
	canvas.create_image(5*data.offset, 15*data.offset, 
		image = data.practiceButton)
	pass


def redrawAll_NORMAL(canvas, data):
	sheetMusic.drawStaff_LEARNING(canvas, data)
	canvas.create_text(data.width // 2, 4*data.offset, 
		text = "My Composition", font = "Arial 24 bold")
	data.music.drawNotesFromMusicList(canvas, data)

	# normal mode play button
	canvas.create_image(5*data.offset, 5*data.offset,
		image = data.playButton_NORMAL)

	color_b = rgbString(128, 139, 150)
	color_t = rgbString(176, 183, 189)
	if data.rightScroll:
		canvas.create_rectangle(data.width - 2*data.offset,
			(data.height - 20*data.offset) // 2, data.width,
			(data.height + 20*data.offset) // 2, fill = color_b,
			width = 0)
		canvas.create_polygon(data.width - 2*data.offset,
			(data.height - 20*data.offset) // 2, data.width - 2*data.offset,
			(data.height + 20*data.offset) // 2, data.width,
			((data.height - 20*data.offset) // 2 + (data.height + 20*data.offset) // 2) // 2,
			width = 0, fill = color_t)
	elif data.leftScroll:
		canvas.create_rectangle(0, (data.height - 20*data.offset) // 2,
			2*data.offset, (data.height + 20*data.offset) // 2,
			fill = color_b, width = 0)
		canvas.create_polygon(2*data.offset, (data.height - 20*data.offset) // 2,
			2*data.offset, (data.height + 20*data.offset) // 2, 0,
			((data.height + 20*data.offset) // 2 + (data.height - 20*data.offset) // 2) // 2,
			width = 0, fill = color_t)
	canvas.create_image(data.width - 5*data.offset, 5*data.offset,
		image = data.saveComposition)
	canvas.create_image(data.width - 5*data.offset, 15*data.offset,
		image = data.openComposition)


def redrawAllHelpScreen(canvas, data):
	cx = data.width // 2
	cy = data.height // 2
	width = data.height * 0.75

	canvas.create_rectangle(cx - (width // 2), cy + (width // 2),
		cx + (width // 2), cy - (width // 2), width = 0, fill = "white")
	canvas.create_text(cx, cy, text = "HOW TO USE:\n1) Choose whether to Compose or Practice\n" +
		"2) To Compose, click the Composition icon!\n\t2a) Click anywhere on the staff to drop" +
		" a note!\n\t2b) To delete the last note, press the delete key!\n\t2c) To save, click " +
		"the Save button!\n\t2d) To open the last save file, click the Read button!\n" +
		"3) To practice, click the Instrument icon!\n\t3a) Click the Music button to hear the " +
		"selection!\n\t3b) To begin practing, click the Conductor icon!", font = "Arial 18")


def redrawAll(canvas, data):
	backgroundColor = rgbString(185,186,187)
	canvas.create_rectangle(0 - data.offset, 0 - data.offset,
		data.width + data.offset, data.height + data.offset,
		width = 0, fill = backgroundColor)
	if (data.MODE == "startScreen"):
		redrawAllStartScreen(canvas, data)
	elif (data.MODE == "helpScreen"):
		if (data.prevMODE == "startScreen"):
			redrawAllStartScreen(canvas, data)
		elif (data.prevMODE == "LEARNING"):
			redrawAll_LEARNING(canvas, data)
		elif (data.prevMODE == "NORMAL"):
			redrawAll_NORMAL(canvas, data)
		redrawAllHelpScreen(canvas, data)
	elif (data.MODE == "LEARNING"):
		redrawAll_LEARNING(canvas, data)
	elif (data.MODE == "NORMAL"):
		redrawAll_NORMAL(canvas, data)

	canvas.create_image(data.width - 4*data.offset,
		data.height - 4*data.offset, image = data.help)
	canvas.create_image(data.width - 12*data.offset,
		data.height - 4*data.offset, image = data.home)
	return

# taken from the class notes
def run(width=300, height=300):
	def redrawAllWrapper(canvas, data):
		canvas.delete(ALL)
		redrawAll(canvas, data)
		canvas.update()    

	def mousePressedWrapper(event, canvas, data):
		mousePressed(event, canvas, data)
		redrawAllWrapper(canvas, data)

	def keyPressedWrapper(event, canvas, data):
		keyPressed(event, data)
		redrawAllWrapper(canvas, data)

	def mouseMotionWrapper(event, canvas, data):
		mouseMotion(event, canvas, data)
		redrawAllWrapper(canvas, data)

	def timerFiredWrapper(canvas, data):
		timerFired(data)
		redrawAllWrapper(canvas, data)
		# pause, then call timerFired again
		canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
	# Set up data and call init
	class Struct(object): pass
	data = Struct()
	data.width = width
	data.height = height
	data.timerDelay = 100 # will be 625 milliseconds for 96 bpm
	# create the root and the canvas
	root = Tk()
	init(data)

	# https://goo.gl/zzqG5l
	#entry = Entry(root)
	#entry.pack()

	canvas = Canvas(root, width=data.width, height=data.height)
	canvas.pack(expand = YES)
	# set up events
	root.bind("<Button-1>", lambda event:
							mousePressedWrapper(event, canvas, data))
	root.bind("<Key>", lambda event:
							keyPressedWrapper(event, canvas, data))
	canvas.bind("<Motion>", lambda event:
							mouseMotionWrapper(event, canvas, data))
	timerFiredWrapper(canvas, data)
	# and launch the app
	root.mainloop()  # blocks until window is closed
	print("bye!")

run(1000, 700)