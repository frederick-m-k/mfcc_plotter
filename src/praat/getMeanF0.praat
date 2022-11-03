form Test command line calls
	text path
	text nameOfWav
endform

Read from file: path$

selectObject: "Sound " + nameOfWav$

To Pitch: 0, 75, 600

selectObject: "Pitch " + nameOfWav$

meanf0 = Get mean: 0, 0, "Hertz"
appendInfoLine: meanf0