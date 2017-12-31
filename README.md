# LeLo - Lego build instruction downLoader

## Purpose
Download building instructions from [lego.com](http://lego.com) and [letsbuilditagain.com](http://letsbuilditagain.com) by set simply entering set id.

Will download per set id if available:
 - product image and build instruction PDF from [lego.com](http://lego.com) 
 - all available images from [letsbuilditagain.com](http://letsbuilditagain.com).   

 
## Usage

Example for set ids 6674 and 547  
`python lelo.py 6674 547` 
 
## Requirements

Python 3.x 

```
pip install lxml 
pip install requests
```

## Ideas & TODOs
* [ ] improve logging / error messages  
* [ ] Craft PDF out of jpeg series

## Notes
* Quick and dirty
* Feel free to improve
