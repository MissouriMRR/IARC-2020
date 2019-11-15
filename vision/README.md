# Vision
The vision team is responsible for processing images in order to extract information relevant to flight control.

## Directory Structure
```
    vision/
        blob/
            ...
            main.py  <- Runnable file
            README.md  <- Feature goal, use instructions
            requirements.txt  <- All necessary pip packages
        realsense/
            ...
            main.py
            README.md
            requirements.txt
        vision_images/  # Downloaded from team drive(see below)
            blob/
            ...
        vision_videos/  # Downloaded from team drive(see below)
            blob/
            ...
        unit_tests/
            blob/
                test_classification.py  <- Follows Unit Testing specs from below
                test_blobbing.py
            ...
            runall.sh  <- Runs every unit test
        main.py  <- Will bootstrap all vision code
        README.md  <- This file.
```


## Images
*Images & Videos should never be commited into any part of the repo at any time!*

Uploading Images & Videos: Upload all content to the MRR Team Drive in *IARC Mission 9/vision_images or videos* then to the respective project folder.

Downloading Images & Videos: From the MRR Team Drive, download *IARC Mission 9/vision_images or videos* and save it in your copy of the repository as *IARC-2020/vision/vision_images (or _videos)*. Code and unit tests should work as if all content is located in these folders.


## Documentation
#### Code Files
```
    """
    At the top of each file you should have a docstring like this describing its purpose.
    """
```

#### Classes
```
    Class Neuron:
        """
        A group of neurons capable of emergent learning.
        
        Parameters
        -----------
        fire_thresh: float
            If a neuron's potential is greater than this value it will fire.
        refactory_period: int
            Time after firing in which neuron cannot fire again.
        """
        def __init__(self, fire_thresh, refactory_period):
            pass
```

#### Functions
```
    def stdp(spike_train):
        """
        An asynchronous hebbian learning rule to suggest synapse weight updates.

        Parameters
        ----------
        spike_train: ndarray[t, n], boolean values
            Log of neuron fires at each timestep.
        
        Raises
        ------
        ValueError: If something bad happens.

        Returns
        -------
        ndarray[n, n] Suggested weight matrix updates.
        """
```

## Unit Testing
All unit testing should be done with the standard python unittest module.

#### Tests Cases
There should be a test case for each major function of each class/function.

```
    import unittest

    class TestNeuron(unittest.TestCase):
        def this_will_not_auto_run(self):
            """
            Functions need to start with test_ to run as unit test.
            """
            print('bark')

        def test_fire(self):
            """
            Testing Neuron.fire.

            Settings
            --------
            Neuron.potential: ndarray[float]
                Currently stored voltage of each neuron.
            Neuron.fire_thresh: float
                Threshold for neurons to fire if potential is greater.

            Returns
            -------
            ndarray[bool] Which neurons have fired and not.
            """
            ## Ensure neurons only fire if potential > fire_thresh
            for fire_thresh in [-np.inf, -15, 0, .1, 100]:  # Need range of test values
                neuron = Neuron(fire_thresh=fire_thresh, 0)
                
                potentials = np.arange(-20, 20, 2)
                neuron.potentials = np.copy(potentials)

                expected_fires = potentials >= fire_thresh

                real_fires = neuron.fire()

                ## only works with python lists
                self.assertListEqual(list(expected_fires), list(real_fires))
    
    
    if __name__ == '__main__:
        unittest.main()
```

#### Mock classes
# Detect Russian Word: 'модули иртибот'
#Download pytesseract for OCR (optical character recognition)

#-----Using Mac and Homebrew-----
#(1) Downlaod tesseract:
		brew install tesseract

#(2) Download tesseract-lang (to use Russian)
		brew install tesseract-lang
#(3) Download Python wrapper
        pip install pytesseract

#-----Using Linux/Windows-----
#(1) Downlaod tesseract and language:
    sudo apt-get install tesseract-ocr-[rus]
#(2) Download Python wrapper
    pip install pytesseract
