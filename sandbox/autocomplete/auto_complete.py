# http://stackoverflow.com/questions/7821661/how-to-code-autocompletion-in-python

import readline # https://pymotw.com/2/readline/
import rlcompleter

class MyCompleter(object):  # Custom completer
    def __init__(self, options):
        self.options = sorted(options)
    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options 
                                    if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]
        # return match indexed by state
        try: 
            return self.matches[state]
        except IndexError:
            return None

completer = MyCompleter(["hello", "hi", "how are you", "goodbye", "great"])
readline.set_completer(completer.complete)
#readline.parse_and_bind('tab: complete') # works on Linux, not Mac OS X

# http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
# see also https://pypi.python.org/pypi/gnureadline, though I didn't install that package
if 'libedit' in readline.__doc__: # detects libedit which is a Mac OS X "feature"
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


input = raw_input("Input: ")
print "You entered", input