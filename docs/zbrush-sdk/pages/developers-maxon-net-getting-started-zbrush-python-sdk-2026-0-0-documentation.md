# Getting Started — ZBrush Python SDK 2026.0.0 documentation

Fonte: https://developers.maxon.net/docs/zbrush/py/2026_0_0/manuals/man_getting_started.html

---

Getting Started — ZBrush Python SDK 2026.0.0 documentation
index
next
|
previous
|
ZBrush Python SDK 2026.0.0 documentation
»
Getting Started
Getting Started
¶
The ZBrush Python API provides a shallow programmatic interface into ZBrush, reflecting most of the ZScript API, while putting all the power of Python at your fingertips.
Note
ZBrush 2026.0.0 ships with Python 3.11.9.
Python in ZBrush
¶
The main entry point to executing Python code in ZBrush is the
ZScript
palette, which also contains the
Python Scripting
subpalette. The Python console of ZBrush can be found at the bottom of the UI.
Fig. I: Shown on the left is the
ZScript
palette, which contains the
Python Scripting
subpalette, as well as the
Script Window Mode
subpalette where you can enable the Python console output. The Python console is shown at the bottom of the ZBrush UI.
¶
Important menu items are:
ZScript Palette
: This palette contains the
Python Scripting
subpalette, which provides access to Python-specific commands and functionalities.
Load
: Loads a Python script file and executes it.
Reload
: Executes the last loaded Python script again.
Clear Output
: Clears the output in the Python console. Note that this won’t scroll the console back to the top. So, if you are scrolled very far down, you might not see the top of the console anymore before you scroll back up.
Script Window Mode
: This allows you to toggle between the default (‘Classic’) output mode and the ‘Python Output’ mode. Without changing the mode, you will not see any Python output in the console.
Tutorial View
: This contains the console of ZBrush and will contain any console output from Python scripts.
Running Python Scripts
¶
working directory:
from
zbrush
import
commands
as
zbc
import
os
print
(
f
"
{
zbc
.
system_info
()
= }
"
)
# print the working dir:
print
(
f
"
{
os
.
getcwd
()
= }
"
)
with
open
(
"system_info.txt"
,
"w"
)
as
f
:
f
.
write
(
zbc
.
system_info
())
Besides the
Load
and
Reload
buttons in the
Python Scripting
subpalette, there exist two more ways to run Python scripts in ZBrush:
Using the Python console: You can enter and execute Python commands interactively in the Python console at the bottom of the UI.
Using the command line: You can run Python scripts from the command line by launching ZBrush with the script as an argument.
ZBrush Python environment
¶
On startup, ZBrush looks for python scripts named
init.py
throughout its
PYTHONPATH
, it will execute all instances found.
As a user, this allows you to have a personal
init.py
script, while having options for an asset, project or studio level ones in larger scale work environments.
ZBrush will also execute all
*.py
files found in the directories defined by the
ZBRUSH_PLUGIN_PATH
environment variable.
ZBrush Python Modules
¶
The following modules are part of the Python integration into ZBrush
zbrush.commands
this module ports the equally-named ZScript commands to python.
zbrush.utils
this module contains various utilities.
Using external python libraries
¶
If you want to use python libraries external to ZBrush in your Python scripts, you will have to add them either to your PYTHONPATH environment variable before starting ZBrush, or add them to the system path by calling
sys.path.append()
from within your Python session.
You can also add the call to
sys.path.append()
to an
init.py
script.
Differences between ZScript and Python
¶
Unlike the ZScript integration, for Python there’s a single interpreter/session created on startup so all actions done during the session are cumulative.
This removes the simplicity of simply “reloading” ZScripts to try out things during development, but it allows for far more complex setups.
To better illustrate the “cumulative” nature of the session, imagine the following example:
“Script A” defines a variable.
“Script B” uses the variable defined by “Script A” to generate another output.
UI Additions
¶
There is now a toggle that allows changing the previously-named “ZScript Tutorial Window” (bottom of the viewport section) to display python output, for this go to the ZScript menu and enable “Script Window Output > ZScript Output”.
There is a new “Python” sub-palette in the ZScript palette that replicates the functionality of the equally-named buttons, but it’s intended for Python use.
Launch Script & Batch
¶
Running scripts on startup that do some automated operations might be needed, for this you can use the launch argument
-script
followed by the python script to execute to get it to run the script as soon as ZBrush is launched.
/path/to/your/ZBrush.exe
-script
/path/to/my_script.py
If you want ZBrush to exit after running the script, you can use the regular python exit approach, like in the following example script:
import
sys
import
zbrush.commands
as
zcmds
zcmds
.
MessageOK
(
"Hello from Python!"
)
sys
.
exit
(
0
)
The above script would start up ZBrush, show an alert message, and upon clicking “Ok” it would continue the execution of the script, exiting ZBrush.
By default, if any error is found during the execution of the script, the error will be caught and displayed in the error log, ZBrush will remain open in the errored state, to get ZBrush to shut down with a process error code add the
-batch
argument e.g:
/path/to/your/ZBrush.exe
-batch
-script
/path/to/my_script.py
All python output is always redirected to terminal if one is attached to the process, this can be useful specially in batch mode.
Getting Started
Python in ZBrush
Running Python Scripts
ZBrush Python environment
ZBrush Python Modules
Using external python libraries
Differences between ZScript and Python
UI Additions
Launch Script & Batch
©
Maxon Computer GmbH
-
End User License Agreement
