<a href="http://www.aerialroboticscompetition.org/">
    <img src="http://www.aerialroboticscompetition.org/assets/images/logo.png" alt="IARC logo" title="IARC" align="right" height="45" />
</a>

# IARC-2020
This repository contains code the Missouri S&T Multirotor Robot Design Team intends to use at the International Aerial Robotics Competition (IARC) in 2020

# Table of contents

- [Codebase Structure](#codebase-structure)
- [Running the Code](#running-the-code)
- [Installation](#installation)
- [Configuration Options](#configuration-options)
- [Contributing](#contributing)
- [License](#license)

## Codebase Structure
```
/vision  # Computer Vision related algorithms
/flight  # Physical control (motors, actuators, etc.) related algorithms
/run.py  # Python program to run the competition code

Information about files within each directory can be found in /<directory>/README.md
```

## Running the Code
To run the competition code
```bash
$ ./run.py  # Run this command
```

## Installation

To run our competition code, you will need:
* A drone or drone [simulator](https://dev.px4.io/master/en/simulation/)
* Python version 3.6 or higher
* Python3 pip
* [Pipenv](https://github.com/pypa/pipenv)

Steps:
1. Install a supported simulator by reading the instructions [here](https://dev.px4.io/master/en/simulation/).
    > Currently, we do simple development with jMAVSim, and complex development and testing in AirSim, so start with jMAVSim

2. Set up the development toolchain. Instructions are platform dependant - more info [here](https://dev.px4.io/master/en/setup/dev_env.html).

3. Clone the PX4 Firmware repository. Tutorial [here](https://dev.px4.io/master/en/setup/building_px4.html#get_px4_code).

4. Install Python3 and pip
  - Recommended installation method is to use [Homebrew](https://brew.sh/) on MacOS `brew install python`, your native package manager on Linux (apt, yum, pacman, rpm), and [the Python website](https://www.python.org/downloads/) on Windows.


## Contributing
1. Clone the repository
```bash
$ git clone https://github.com/MissouriMRR/IARC-2020
```
2. Make sure you are on the up to date `develop` branch.
```
$ git switch develop
$ git pull
```
2. Create a branch to add your changes by running.
```
$ git switch -c "branch_name"
```
> `branch_name` should follow the convention `feature/{feature_name}`, or `hotfix/{fix_name}`
3. Make changes in your new branch and commit regularly.
4. Once changes are complete, go to GitHub and submit a "Pull Request". Fill in necessary information. Any issues your PR solves should be donoted in the description by putting the words `Closes #99` where `99` is replaced with the issue you are closing. Request one of the software leaders to review the PR on the right hand side of the PR.
5. Once it has been reviewed by other members of the team, it can be accepted to the `develop` branch and the cycle continues...

> More info on the process [here](https://nvie.com/posts/a-successful-git-branching-model/) and [here](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

## License

We adopt the MIT License for our projects. Please read the [LICENSE](https://github.com/MissouriMRR/IARC-2020/blob/master/LICENSE) file for more info
