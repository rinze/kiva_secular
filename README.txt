kiva_secular
============

This little project uses Python to generate a static HTML webpage that lists
Kiva projects loans by non-religious organizations.  

The list of non-religious organizations is taken from a list created by the
Kiva Atheists group available at http://www.tinyurl.com/AASFSHNR-MFIs

You can see a demo version (updated every hour) on
http://www.eurielec.etsit.upm.es/~chema/kiva_secular/

Feel free to create your own mirror! Just download the latest release and run
in a cron job:

$ python kiva_secular.py > index.html

Then copy the index.html and styles.css files to a directory with web access,
and you're all set.
