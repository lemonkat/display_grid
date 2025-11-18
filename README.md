# display_grid

display_grid is a library I made for the purpose of making terminal UIs. It's used in many of my other projects, such as my upcoming rhythm game. 

display_grid's primary layer of abstraction is the `Grid`, representing a section of the screen. A `Grid` contains NumPy arrays representing the characters, text and background colors, and formatting attributes for that region of the screen.

`Grid` objects can either draw on a terminal using `urwid`, or draw to a display window using `pygame`. This means you can make a terminal UI, but if someone can't easily use a terminal then they have another option.

Hope you find this useful for something!