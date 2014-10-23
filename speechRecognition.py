
import speech_recognition as sr
r = sr.Recognizer()
with sr.WavFile("/Volumes/1/E6998_testing/CUE6998_2014_09-20140929/vf9-29.wav") as source:              # use "test.wav" as the audio source
    audio = r.record(source)                        # extract audio data from the file

try:
    print("You said " + r.recognize(audio))         # recognize speech using Google Speech Recognition
except KeyError:                                    # the API key didn't work
    print("Invalid API key or quota maxed out")
except LookupError:                                 # speech is unintelligible
    print("Could not understand audio")

'''
from pygsr import Pygsr

speech = Pygsr()
speech.record(3) # durationin seconds (3)
phrase, complete_response =speech.speech_to_text('en_US') # select the language
print phrase
'''