# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask003.html

import model
import view

model.r = view.get_input()
view.present_output(model.r)
