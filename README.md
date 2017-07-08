# Simplenote Artist Database (SNAD)
Use a list on Simplenote to keep track of artists that you like on Danbooru (or
really, keep track of anything from anywhere).

I made this because I found myself hoarding a list of artists (for...science)
and manually searching using the official Electron app, scrolling to the bottom
of the list and retyping what I put in the search bar was tedious and I was
repeating myself. Repeating yourself is bad, so now these scripts exist.
However, I have broken my bad habit of needlessly storing names, and so this
repo is pretty much unmaintained now.

## Usage
Simply call `snad` with the thing you want to append to the list. The program
will automatically search it to ensure there are no duplicates, and if it isn't
already there, your input will be added. See `snad --help` for more info.

`padd` also exists, to delete things from the list(s). Same usage applies.

## TODO
* Allow user to choose which note to append to, rather than forcing the scripts
to be used for the oddly specific need to remember Danbooru artist entries.
