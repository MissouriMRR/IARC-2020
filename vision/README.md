# Vision

The vision team is responsible for processing images in order to extract information relevant to flight control.

## Quick Links

[Getting Started](#getting-started)

[Directory Structure](#directory-structure)

[Competition Algorithms](#competition-algorithms)

[Storing Images](#storing-images)

[Documentation](#documentation)

[Unit Testing](#unit-testing)

[Benchmarking](#benchmarking)

## Getting Started

1.  Clone this repository

```bash
    git clone https://github.com/MissouriMRR/IARC-2020
```

2.  Install pip requirements

```bash
    pip install -r requirements.txt
```

3.  (Optional, for benchmarks) Download the test images from the team drive, [details](#storing-images).

4.  (Optional) Run unit tests.

```bash
    ./unit_tests/runall.sh
```

5.  Contributing

    5a. Go to the [Projects section of the repository.](https://github.com/MissouriMRR/IARC-2020/projects)

    5b. In any project, choose an issue from the To do section.

    5c. Create a plan for solving this issue and get approved by leadership.

    5d. Checkout respective branch in repository and write code.

    5e. When finished, go to the repository website and submit a pull request.

    5f. Have pull request reviewed.

    5g. Merge branch into develop when approved.

## Directory Structure

```
    vision/
        module/  # Tasks relating to the module block
            get_module_depth.py  <- Code, usable in IARC-2020/vision/pipeline.py
            ...
            README.md

        obstacle/  # Tasks relating to obstacle detection
            ...
            README.md  <- Feature goal, use instructions

        pylon/  # Tasks relating to the pylon
            ...
            README.md

        text/  # Tasks relating to text detection
            ...
            README.md

        camera/  # Tasks relating to the camera
            ...
            README.md

        common/  # Common vision tools
            blob_plotter.py
            ...

        tools/  # Tools for use in vision testing
            blob_annotator/
                ...
                main.py
            record_video.py
            view_depth.py

        vision_images/  # Downloaded from team drive (see below)
            obstacle/
            ...

        vision_videos/  # Downloaded from team drive (see below)
            obstacle/
            ...

        bounding_box.py  <- Class for formatting vision output
        interface.py  <- For modeling the environment around the drone
        pipeline.py  <- Will bootstrap all vision code
        README.md  <- This file.
        requirements.txt  <- All necessary pip packages

        benchmarks/
            accuracy/
                __init__.py
                bench_module.py  <- Follows Benchmarking Guides
                ...
                runall.py
            times/
                __init__.py
                bench_module.py  <- Follows Benchmarking Guides
                ...
                runall.py
            common.py
            README.md  <- Instructions for Benchmarks

        unit_tests/
            test_camera.py  <- Follows Unit Testing specs from below
            test_obstacle.py
            ...
            runall.sh  <- Runs every unit test
```

## Competition Algorithms

There are 3 main branches of vision code that can be used for competition: obstacle, text, and module.
The goal of obstacle algorithms is to identify obstacles as the drone flies around the pylons.
The goal of text algorithms is to detect the cyrillic text located on the mast.
The goal of module algorithms is to identify the module located on the mast, including its location, depth, and orientation.

Vision algorithms are run from `pipeline.py`. The pipeline will be called from flight in order to retrieve
bounding boxes obtained by vision algorithms.

Vision algorithms can also be run from `benchmarks/run_bench.py` for testing purposes.

## Storing Images

*Images & Videos should never be commited into any part of the repo!*

Uploading Images & Videos: Upload all content to the MRR Team Drive in *IARC Mission 9/vision_images or videos* then to the respective project folder.

Downloading Images & Videos: From the MRR Team Drive, download *IARC Mission 9/vision_images or vision_videos* and save the zip file. Extract its contents into your copy of the repository as *IARC-2020/vision/vision_images (or vision_videos)*.

## Documentation

### Modules

```python
    """
    At the top of each file you should have a docstring like this describing its purpose.
    """
```

### Classes

```python
    class SpikingNeuron:
        """
        A group of neurons with temporal dynamics.

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

### Functions

```python
    def stdp(spike_train):
        """
        An asynchronous hebbian learning rule that suggests synapse weight updates.

        Parameters
        ----------
        spike_train: ndarray[t, n] w/ boolean values
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

### Tests Cases

There should be a test case for each major function of each class/function.

```python
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

                self.assertListEqual(list(expected_fires), list(real_fires))


    if __name__ == '__main__:
        unittest.main()
```

### Mocking

When testing a class and its methods, it's important to know if failed tests are caused by the object itself or those it relies on. Mock classes/functions are used to overload any other functionality defined in the project that the class/function being tested relies on. This way, if a unit test fails, it is clear what class/function caused this issue.

#### Mock functions

```python
    import unittest
    from unittest import mock

    class TestInputNeuron(unittest.TestCase):
        def test_tick(self):
            """
            Testing InputNeuron.__call__.

            Parameters
            ----------
            state: tuple
                Current state of env.

            Returns
            -------
            ndarray Spikes fired in input neurons.

            Effects
            -------
            InputNeuron calls get_rates w/ state as parameter, using the output to set input rate.
            """
            ## Ensure get_rates called w/ correct params.
            states = [('a', 'b'), None]

            for state in states:
                get_rate = mock.Mock(return_value=.5)

                neuron = InputNeuron(get_rate)
                neuron(state)

                get_rate.assert_called_once()

                call_args = list(get_rate.call_args)
                self.assertEqual(len(call_args), 1)
                self.assertIn(state, call_args)

            ## ...


    if __name__ == '__main__:
        unittest.main()
```

#### Mock classes

```python
    import unittest
    from unittest import mock

    class TestNeuralNetwork(unittest.TestCase):

        def test_reset(self):
            """
            Testing NeuralNetwork.reset.

            Effects
            -------
            Neuron.reset is called with parameters x, y, z.
            Synapse.reset is called with parameters z, y, x.
            """
            ## Ensure Neuron & Synapse reset functions called w/ correct params.

            # -> assumes NeuralNetwork has imports for neuron, synapse
            with mock.patch('Neuron', spec=Neuron) as mock_neuron:
                with mock.patch('Synapse', spec=Synapse) as mock_synapse:
                    network = NeuralNetwork()

                    mock_neuron.reset.assert_called_once()
                    mock_synapse.reset.assert_called_once()

                    neuron_call_args = list(mock_neuron.reset.call_args)
                    self.assertEqual(len(neuron_call_args), 3)
                    self.assertIn('x', neuron_call_args[0])
                    # ...

                    synapse_call_args = list(mock_synapse.reset.call_args)
                    self.assertEqual(len(synapse_call_args), 3)
                    self.assertEqual('z', synapse_call_args[0])
                    # ...


    if __name__ == '__main__:
        unittest.main()
```

## Benchmarking

The folder *benchmarks/* contains tools to gauge the time and accuracy of vision algorithms per different image categories, i.e. poor lighting, noisey background, ... Information to configure and make use of these can be found in *[benchmarks/README.md](https://github.com/MissouriMRR/IARC-2020/blob/feature/vision_docs/vision/benchmarks/README.md)*.
