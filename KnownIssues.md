# Known Issues

Please search the page. The errors are described and discussed in no particular order. 

#### Failed to find edges

One possible reason can be that Excel file is open in the background. Close edge file if opened in background. 

#### Parser Error: LXML missing when using import_from_gridlabd()

You need to install LXML. The easiest is to `pip install lxml`. If it does not work, and if you are on Windows, go to [this page](https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml) and download the latest version of LXML, which is appropriate for your platform. It will be a *.whl file. Then you can go to the folder where you downloaded the *.whl file, and simply do:

  ```
    pip install <file-name-you-download>.whl
  ```

If you are using an Unix operating system, take a look at [this page](http://lxml.de/installation.html). 


####  Updated installation, but still old errors remain.
  
This is probably due to the cache of the `egg` file. If you are using Windows and Python 3.6.x, you can fix it by going here in a Folder:

  ```
  C:\Users\<YOUR-USER-NAME>\AppData\Local\Programs\Python\Python36-32\Lib\site-packages
  ```

  and deleting the old pyCanvass egg file in favor of the latest version. Note that the latest version has a higher number at the end of the version number compared to the older version. 

####  Visualization Error

In Windows, if you see the no module 'tkinter' error, just download a binary installer for python. Open the installer, and select 'Modify'. When the program starts, make sure to click to install tcl/tk this time. 

