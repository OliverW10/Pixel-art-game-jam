import cx_Freeze

executables = [cx_Freeze.Executable("main.py")]

#set TCL_LIBRARY=C:\Program Files\Python36\tcl\tcl8.6
#set TK_LIBRARY=C:\Program Files\Python36\tcl\tcl8.6

cx_Freeze.setup(name = "some ship",
	options={"build_exe": {"packages":["pygame", "json", "numpy"], "include_files":[]}},
	executables = executables
	)