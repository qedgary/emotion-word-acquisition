# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 10:47:59 2020

@author: Gary Zhang
"""

praatRawFormants = input("Enter the data, copied and pasted directly from Praat:\n-----------------------------\n")

# delete header row, if present
if "F4_Hz" in praatRawFormants:
   praatRawFormants = praatRawFormants[praatRawFormants.index("F4_Hz") + 6:]
   
praatRawFormants = praatRawFormants.replace("--undefined--","-100").split()

Time = []
F1   = []
F2   = []
F3   = []

for k in range(0,len(praatRawFormants), 5):
   Time.append(float(praatRawFormants[k]))

for k in range(1,len(praatRawFormants), 5):
   F1.append(float(praatRawFormants[k]))

for k in range(2,len(praatRawFormants), 5):
   F2.append(float(praatRawFormants[k]))
   
for k in range(3,len(praatRawFormants), 5):
   F3.append(float(praatRawFormants[k]))

F1_moving = sum(F1[0:6]) / 6
F2_moving = sum(F2[0:6]) / 6
F3_moving = sum(F3[0:6]) / 6

cutoff = 200 # frequency difference, in Hertz, where we declare the diphthong's first vowel ends
cutoffTime = 0

# compute CUMULATIVE moving averages
for n in range(len(Time)):
   F1_now = F1[n] # get current value of formant
   F2_now = F2[n]
   F3_now = F3[n]
   
   # if the current frequency goes too far away from the movign average...
   if (n > 3 and
      (F1_now - F1_moving > cutoff or F1_now - F1_moving < -cutoff or 
       F2_now - F2_moving > cutoff or F2_now - F2_moving < -cutoff#or 
       #F3_now - F3_moving > cutoff or F3_now - F3_moving < -cutoff
      )):
      cutoffTime = Time[n]
      break # ...then we stop measuring
   
   if (n > 6):
      F1_moving = sum(F1[0:n + 1]) / (n + 1)
      F2_moving = sum(F2[0:n + 1]) / (n + 1)
      F3_moving = sum(F3[0:n + 1]) / (n + 1)


print("-----------------------------")
print("Start time: " + str(Time[0]) + "   End time: " + str(cutoffTime))

print("Copy and paste the data below into the colored boxes of the spreadsheet:\n-----------------------------")
print(F1_moving)
print(F2_moving)
print(F3_moving)

if cutoffTime - Time[0] < 0.04:
   print("Warning! Your data selection may have started too early, and included \n" +
         "parts of the preceding consonant. You may get a more accurate result if \n" +
         "you move the start of your selection to a slighly later duration. You \n" +
         "can alternatively exclude the first few lines of formants when you \n" +
         "copy-and-paste them into this script. It is also possible you are \n"+
         "getting this message in error. For example, if the red dots suddenly \n" +
         "jump around noisily in Praat, you may want to click \"formant settings\" \n" +
         "and set your window length to 0.04 s. If the red dots disappear, you may\n"+
         "want to exclude parts where they disappear from your selection.")










