# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 10:47:59 2020

@author: Gary Zhang
"""
# copy and paste your raw Praat output into the string below (trailing/leading whitespace is okay).
# In this new version, you'll simply paste in Praat's formants into praatRowFormants, then run the
# code, instead of running the code first, then pasting into standard input.
praatRawFormants = """

Time_s   F1_Hz   F2_Hz   F3_Hz   F4_Hz
4.469162   767.272274   1130.539091   2547.412496   3986.888087
4.479162   755.607777   1123.588938   2542.155204   3978.497052
4.489162   621.645124   1121.639920   2467.974779   3932.335406
4.499162   616.623982   1114.396977   2466.490256   4284.056287
4.509162   723.559874   1020.921530   2414.649687   4015.462404
4.519162   761.399337   1013.568828   2444.435770   3783.833682
4.529162   760.230350   1102.257512   2462.408313   3832.199506
4.539162   783.099080   1094.400436   2414.710217   3975.547480
4.549162   800.355251   1111.515518   2457.577737   4049.720375
4.559162   815.615641   1119.191457   2489.012645   4076.643396

"""

if type(praatRawFormants) == type([]):
   praatRawFormants = "\n".join(praatRawFormants)

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
# we were going to do 60 Hz, but then I actually tried this and realized it was a terrible idea
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
       # basically, I found that F3 doesn't really work well for this... why though, I don't know
      )):
      cutoffTime = Time[n]
      break # ...then we stop measuring
   if n == len(Time) - 1:
      cutoffTime = Time[n]

   if (n > 6): # re-compute moving average, but don't let earliest measurements skew the entire average
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
