import shelve

elist = {
	'Badzmiek': ("Karolina Badzmierowska", "KB"),
	"Bleierr": ("Roman Bleier", "RB"),
	"RB": ("Roman Bleier", "RB"),
	"Brhughes": ("Brian Hughes", "BH"),
	"Emma": ("Emma Clarke", "EC"),
	"HannahH" : ("Hannah Healy", "HH"),
	"HH" : ("Hannah Healy", "HH"),
	"Linda" : ("Linda Spinazzè", "LS"),
	"NealeRo": ("Neale Rooney", "NR"),
	"NR": ("Neale Rooney", "NR"),
	"Schreibs": ("Susan Schreibman", "SS"),
	"SS": ("Susan Schreibman", "SS"),
	"William.buck": ("William Buck", "WB"),
	"badzmiek": ("Karolina Badzmierowska", "KB"),
	"VDG": ("Vinayak Das Gupta", "VDG"),
	"Mfar": ("Mel Farrell", "MF"),
	"Oculardexterity": ("Richard Hadden", "RH"),
	"Roman": ("Roman Bleier", "RB"),
	"Smcgarry": ("Shane McGarry", "SMG"),
	"lindaspinazze": ("Linda Spinazzè", "LS"),
	"Precaurious": ("Linda Spinazzè", "LS"),
	"Vinayak": ("Vinayak Das Gupta", "VDG")
}

with shelve.open('editorList.shelve') as shelf:
	for k, v in elist.items():
		shelf[k] = v