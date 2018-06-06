# Known Issues

#####  Updated installation, but still old errors remain.
  
This is probably due to the cache of the `egg` file. If you are using Windows and Python 3.6.x, you can fix it by going here in a Folder:

  ```
  C:\Users\<YOUR-USER-NAME>\AppData\Local\Programs\Python\Python36-32\Lib\site-packages
  ```

  and deleting the old egg file in favor of the latest version. Note that the latest version has a higher number at the end of the version number compared to the older version. 


##### Failed to find edges

One possible reason can be that Excel file is open in the background. Close edge file if opened in background. 


#####  Visualization Error

In Windows, if you see the no module 'tkinter' error, just download a binary installer for python. Open the installer, and select 'Modify'. When the program starts, make sure to click to install tcl/tk this time. 