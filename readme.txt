Install Python
==============
1. goto python.org
2. download and install Python >= 3.10 (=> on Windows: advisable to install Python on C: drive)



Install missing modules
=======================
1. start bash/cmd.exe with admin privileges
2. run: pip install pyqt6



Run program (3 versions)
========================
- run with Python: start.py
- on Windows run start_scheduler.bat
- on Windows cd to folder containing files and type in cmd.exe: python.exe -OO start.py



Verify
======
The program should look like in screenshot scheduler_0.png (in the program folder)



Idea
====
Check out screenshots scheduler_1.png and scheduler_2.png for a general guide on which button does what. In the following are explanations of all important functions. Compare to the two screenshots.

In general, the idea is to have one week loaded. Long periods of time can be loaded too, but the program is not too fast, so tread carefully.

Don't turn off the program without stopping the timer first. If it happens you need a db tool to fix it (Ask me, I will tell you how).

Timer:
-----
On the left edge of the tool is the timer. It has a small, red cross on top. If pressed, it reverses anything that is running to stop state.

The 'Calendar' Icon and the displayed date are deprecated. The tool used to consist only of the timer, later the scheduler part and the todo list were added.

The 'Cross' icon can be used to minimize the tool to the timer bar (make schedule, time table, todo list and summary disapear). Press the icon in the same place to restore the view.

In the dropdown, select which lecture the time will be booked on.

Press the 'stop' button to terminate recording time and stop.

Press the 'red' button to start recording work time. This time will be colored in red in the scheduler view.

Press the 'blue' button for break time. This time will be shown in blue on the scheduler view.

Press the 'green' button for coffee time. Coffee time is generally deprecated. The idea was to record lunch times and things like that without having it influence statistics. This time will be shown in green on the scheduler view.

Todo list:
----------
On top left of the tool is a todo list where items can be added, checked off, erased and moved up and down. The todo list has no interaction with anything else in the tool and is not very usefull

Schedule view:
--------------
On the top right of the tool is the schedule view. New entries can be made by draging the pressed mouse over the relevant time interval. After the user releases the mouse, a menu shows up where the user can select the type of the entry (Lecture, Exercise, Coffe and Free work). Note that 'Coffee' is deprecated (don't use). At the top of the menu is a checkbox 'scheduled'. If checked, the tool will create the same entry every week on the same day between the two dates 'From' and 'To' (note that the entry fields for the dates are a bit stupid, just don't give up...).

It is possible to 'book' time later on. Select one of the scheduled boxes, then the menu appears, then press 'Book Time' or 'Delete Time' to reverse the booking. It is not possible to delete a scheduled box that has time booked on it.

Remember that there are 3 types of scheduled boxes: Lecture, Exercise and Free Work. The manual time booking (Book Time) for the first two creates a gray bar, for the Free Work, the bar looks the same as with the regular timer. NOTE: there is a bug there: if the manual booking is used with Lecture or Exercise, the bars in the summation box on the bottom left will not be updated immediately, with Free Work, it will. If the tool is restarted, the bars will look correct though. I will fix this later.

Time summary
------------
On the bottom left are the recorded times per subject, summed up over the entire selected interval in the schedule view. The gray bar indicates planed time, the green bar indicates recorded time. The fat number on the right is the same as the regular numbers inside the bars (they used to be different, but aren't anymore)

The two fat bars at the bottom are the summation over all subjects during the selected time interval.

Time table
----------
On the bottom right is the time table. The user can insert PLANING times by hand (click on one of the cells and enter a number, press Alt+directional keys to move between cells faster). NOTE: there is a bug here somewhere, if you change cells too quickly, the program may crash. No idea where the bug is, just live with it.

One entry looks like [1.9    1.9/2.0]. Only the right hand side numbers are relevant. The fat one is redundant. The format is [recorded time / planed time]. Each cell will color itself from red to green based on how much the deviation is between the two.

On the bottom of the time table are the summations per day in the same format.



Known bugs
==========
- if the user switches between cells of the time table too quickly while adding new times to each cell, the program may crash
- scrolling in the schedule view only works while the mouse is on the time axis or besides the sheet with the scheduled boxes. Best to use the scroll bar
- scrolling the schedule view too quickly will mess up the edges (Python is probably too slow)
- manual booking of time for schedule boxes of type Lecture and Exercise does not update the time summary properly (restart program or minimize to timer and back to update)
- the entire program is not excessively quick



Move DB to somewhere else (like into polybox for automatic sync to other computers)
===================================================================================
1. create dbconfig.txt inside the scheduler program's folder
2. write complete, absolute path into file (like C:\Users\LoL\Documents\polybox\python_scheduler_db/data.db)
3. check that you wrote /data.db at the end of the path
4. run scheduler
