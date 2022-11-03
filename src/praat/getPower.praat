form Power command line calls
	text wavPath
	text wavFileName
	positive start
    positive end
endform

Read from file: wavPath$

selectObject: "Sound " + wavFileName$

power = Get energy: start, end
appendInfoLine: power