#### Features
Methods for representing geographic coordinates (latitude and longitude) including the ability to:

> * Convert lat/lon strings from almost any format into a LatLon object (analogous to the datetime library’s stptime method)
> * Automatically store decimal degrees, decimal minutes, and degree, minute, second information in a LatLon object
> * Output lat/lon information into a formatted string (analogous to the datetime library’s strftime method)
> * Project lat/lon coordinates into some other proj projection
> * Calculate distance and heading between lat/lon pairs using either the FAI or WGS84 approximation
> * Create a new LatLon object by offsetting an initial coordinate by a distance and heading
> * Subtracting one LatLon object from another creates a GeoVector object with distance and heading attributes (analogous to the datetime library’s timedelta object)
> * Adding or subtracting a Latlon object and a GeoVector object creates a new LatLon object with the coordinates adjusted by the GeoVector object’s distance and heading
> * GeoVector objects can be added, subtracted, multiplied or divided

#### Installation
LatLon has only been tested in Python 2.7, 3.6

Installation through pip:

```bash
$ pip install LatLon
```

Requires the following non-standard libraries:

> * pyproj

#### Usage Notes
Usage of LatLon is primarily through the class LatLon, which is designed to hold a single pair of Latitude and Longitude objects. Strings can be converted to LatLon objects using the method string2latlon, and to Latitude or Longitude objects using string2geocoord. Alternatively, a LatLon object can be constructed by subtracting two LatLon objects, or adding or subtracting a Latlon object and a GeoVector object.

##### Latitude or Longitude Construction
Latitude of longitude construction is through the classes Latitude and Longitude, respectively. You can pass a latitude or longitude coordinate in any combination of decimal degrees, degrees and minutes, or degrees minutes and seconds. Alternatively, you can pass a formatted string using the function string2geocoord for a string containing a single latitude or longitude, or string2latlon for a pair of strings representing the latitude and longitude.

##### String formatting:
string2latlon and string2geocoord both take a formatter string which is loosely modeled on the format keyword used in datetime’s strftime function. Indicator characters (e.g. H or D) are placed between a specific separator character (%) to specify the way in which a coordinate string is formatted. Possible values are as follows:

> * H is a hemisphere identifier (e.g. N, S, E or W)
> * D is a coordinate in decimal degrees notation (e.g. 5.833)
> * d is a coordinate in degrees notation (e.g. 5)
> * M is a coordinate in decimal minutes notation (e.g. 54.35)
> * m is a coordinate in minutes notation (e.g. 54)
> * S is a coordinate in seconds notation (e.g. 28.93)
> * Any other characters (e.g. ‘ ‘ or ‘, ‘) will be treated as a separator between the above components.
> * All components should be separated by the % character. For example, if the coord_str is ‘5, 52, 59.88_N’, the format_str would be ‘d%, %m%, %S%_%H’

##### Important
One format that will not currently work is one where the hemisphere identifier and a degree or decimal degree are not separated by any characters. For example ‘5 52 59.88 N’ is valid whereas ‘5 52 59.88N’ is not.

##### String output:
Both LatLon and Latitude and Longitude objects include a to_string() method for outputting a formatted coordinate.

##### Projection:
Use LatLon.project to transform geographical coordinates into a chosen projection. Requires that you pass it a pyproj or basemap projection.

##### Distance and Heading Calculation:
LatLon objects have a distance() method which accepts a 2nd LatLon object as an argument. distance() will calculate the great-circle distance between the two coordinates using the WGS84 ellipsoid by default. To use the more approximate FAI sphere, set ellipse to ‘sphere’. Initial and reverse headings (in degrees) can be calculated in a similar way using the heading_initial() and heading_reverse() methods. Alternatively, subtracting one LatLon object from another will return a GeoVector object with the attributes heading and distance.

##### Creating a New LatLon Object by Offset from Another One:
Use the offset() method of LatLon objects, which takes an initial heading (in degrees) and distance (in km) to return a new LatLon object at the offset coordinates. Also, you can perform the same operation by adding or subtracting a LatLon object with a GeoVector object.

#### Examples
Create a LatLon object from coordinates:

```python
>> palmyra = LatLon(Latitude(5.8833), Longitude(-162.0833)) # Location of Palmyra Atoll in decimal degrees
>> palmyra = LatLon(5.8833, -162.0833) # Same thing but simpler!
>> palmyra = LatLon(Latitude(degree = 5, minute = 52, second = 59.88),
>>                  Longitude(degree = -162, minute = -4.998) # or more complicated!
>> print(palmyra.to_string('d% %m% %S% %H')) # Print coordinates to degree minute second
('5 52 59.88 N', '162 4 59.88 W')
```

Create a Latlon object from a formatted string:

```python
>> palmyra = string2latlon('5 52 59.88 N', '162 4 59.88 W', 'd% %m% %S% %H')
>> print(palmyra.to_string('d%_%M')) # Print coordinates as degree minutes separated by underscore
('5_52.998', '-162_4.998')
```

Perform some calculations:

```python
>> palmyra = LatLon(Latitude(5.8833), Longitude(-162.0833)) # Location of Palmyra Atoll
>> honolulu = LatLon(Latitude(21.3), Longitude(-157.8167)) # Location of Honolulu, HI
>> distance = palmyra.distance(honolulu) # WGS84 distance in km
>> print distance
1766.69130376
>> print(palmyra.distance(honolulu, ellipse = 'sphere')) # FAI distance in km
1774.77188181
>> initial_heading = palmyra.heading_initial(honolulu) # Heading from Palmyra to Honolulu on WGS84 ellipsoid
>> print(initial_heading)
14.6907922022
>> hnl = palmyra.offset(initial_heading, distance) # Reconstruct Honolulu based on offset from Palmyra
>> print(hnl.to_string('D')) # Coordinates of Honolulu
('21.3', '-157.8167')
```

Manipulate LatLon objects using GeoVectors:

```python
>> vector = (honolulu - palmyra) * 2 # A GeoVector with 2x the magnitude of a vector from palmyra to honolulu
>> print(vector) # Print heading and magnitude
14.6907922022 3533.38260751
print(palmyra + (vector/2.0)) # Recreate the coordinates of Honolulu by adding half of vector to palmyra
21.3, -157.8167
```

#### Version
1.0.2 - Tested on Python 2.7 with Eclipse IDLE. Please let me know of any issues.

#### Changelog

##### 1.0.3 (June/16/2019)
> * Support for Python 2.7 and Python 3

##### 1.0.2 (OCTOBER/14/2014)

> * Class GeoVector is now an abstract class to ensure that any subclasses use the correct API
> * Added methods range180 and range360 to class Longitude to interconvert between longitudes reported -180 to 180 format and those reported in 0 to 360 format. To ensure that all operations such as hemisphere assignment work as expected, longitudes reported in 0 to 360 format are automatically converted into -180 to 180 format when the Longitude object is initialized.

##### 1.0.1 (SEPTEMBER/2/2014)

> * Fixed issue with where attribute theta in GeoVector was treated in some cases like a heading (i.e. starting with due north and continuing clockwise) even though it was in fact an angle (i.e. starting with (1, 0) and continuing anti-clockwise). The attribute name has now been changed to heading to eliminate confusion. The local variable theta is used for computations involving angle.
> * Added testing functions with pytest for class LatLon and GeoVector
> * Added almost_equal methods to class LatLon and GeoVector to deal with float errors in decimal degree specification
> * LatLon.project now returns (x, y) instead of (y, x) to be more consistent with the accepted convention.

##### 0.91 (AUGUST/28/2014)

> * degree, minute and second attributes for GeoCoord class are now coerced to type float

##### 0.90 (AUGUST/28/2014)

> * Updated magic methods for GeoCoord class
> * Added option for instantiating LatLon from scalars

##### 0.80 (AUGUST/27/2014)

> * Added GeoVector class to handle vectors between two LatLon objects
> * Cleaned up __str__ and __repr__ methods for LatLon, Latitude, Longitude, GeoCoord, and GeoVector classes

##### 0.70 (AUGUST/27/2014)

> * Deprecated LatLon.distance_sphere method. From now on use distance(other, ellipse = ‘sphere’) instead
> * Added LatLon.bearing method to return the initial bearing between two LatLon objects
> * Added LatLon.offset method to return a new LatLon object that is computed from an initial LatLon object plus a bearing and distance

##### 0.60 (AUGUST/27/2014)

> * Added compatibility with comparison, negation, addition and multiplication magic methods

##### 0.50 (AUGUST/20/2014)

> * First release