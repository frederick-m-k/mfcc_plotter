form createMFCC command line calls
	text wavPath
	text wavFileName
	text mfccFilePath
	real n_mfccs
	real window_size
	real time_step
	real first_filter_freq
	real filter_distance
	real max_filter_freq
endform

Read from file: wavPath$

selectObject: "Sound " + wavFileName$

To MFCC: n_mfccs, window_size, time_step, first_filter_freq, filter_distance, max_filter_freq

selectObject: "MFCC " + wavFileName$

Save as text file: mfccFilePath$