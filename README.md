<a href="http://www.aerialroboticscompetition.org/">
    <img src="http://www.aerialroboticscompetition.org/assets/images/logo.png" alt="IARC logo" title="IARC" align="right" height="50" />
</a>

# IARC-2020

This repository contains code the Missouri S&T Multirotor Robot Design Team
intends to use at the International Aerial Robotics Competition (IARC) in 2020

## Table of Contents

- [Codebase Structure](#codebase-structure)
- [Running the Code](#running-the-code)
- [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)

## Codebase Structure

```text
/vision  # Computer Vision related algorithms
/flight  # Physical control (motors, actuators, etc.) related algorithms
/run.py  # Python program to run the competition code

Information about files within each directory can be found in /<directory>/README.md
```

## Running the Code

To run the competition code

```bash
pipenv shell # Initialize the python environment
./run.py  # Run the code
```

## Requirements

To run our competition code, you will need:

- A drone or drone [simulator](https://dev.px4.io/master/en/simulation/)
- Python version 3.6 or higher
- [pipenv](https://github.com/pypa/pipenv)
- [MAVSDK-Python](https://github.com/mavlink/MAVSDK-Python)

## Installation

1. Set up the development toolchain. Instructions are platform dependant - more
   info [here](https://dev.px4.io/master/en/setup/dev_env.html#development-environment).
    - Choose your operating system from the **Development Environment** section
    - **Install the latest Python version** using [pyenv](https://github.com/pyenv/pyenv)
       on MacOS and Linux. For Windows, get the executable from [the Python website](https://www.python.org/downloads/).
    - Make sure you follow the steps *very specifically* - else you will waste time.

2. Install [pipenv](https://github.com/pypa/pipenv)

3. Clone the PX4 Firmware repository. Tutorial [here](https://dev.px4.io/master/en/setup/building_px4.html#get_px4_code).

4. If you are testing at home, install a supported simulator by reading the
   instructions [here](https://dev.px4.io/master/en/simulation/jmavsim.html).
    - Currently, we do simple development with jMAVSim, and complex development
      and testing in AirSim, so start with jMAVSim
    - Run the make command in the PX4 Firmware repository

5. In the root of this repository, run the following to create a virtual
   environment and install our packages:

    ```bash
    pipenv install
    ```

## Contributing

1. Clone the repository

    ```bash
    git clone https://github.com/MissouriMRR/IARC-2020
    ```

2. Make sure you are on the up to date `develop` branch.

    ```bash
    git switch develop
    git pull
    ```

3. Create a branch to add your changes by running.

    ```bash
    git switch -c "branch_name"
    ```

    > `branch_name` should follow the convention `feature/{feature_name}`, or `hotfix/{fix_name}`

4. Make changes in your new branch and commit regularly.

5. Once changes are complete, go to GitHub and submit a "Pull Request". Fill in
   necessary information. Any issues your PR solves should be donoted in the
   description by putting the words `Closes #99` where `99` is replaced with the
   issue you are closing. Request one of the software leaders to review the PR
   on the right hand side of the PR.

6. Once it has been reviewed by other members of the team, it can be accepted to
   the `develop` branch and the cycle continues...

    > More info on the process [here](https://nvie.com/posts/a-successful-git-branching-model/)
      and [here](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

## License

We adopt the MIT License for our projects. Please read the [LICENSE](https://github.com/MissouriMRR/IARC-2020/blob/master/LICENSE)
file for more info

