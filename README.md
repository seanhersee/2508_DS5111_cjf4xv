Prerequesits:
  - Ubuntu setup on AWS EC2 Instance
  - Configured SSH Key for Github


Step #1: Virtual Machine Setup

1) Create a Reproducable Setup Script

  - create a file called "init.sh"
     `nano init.sh`
  - add the following setup steps
  ```Bash
    sudo apt update
     sudo apt install make -y
     sudo apt install python3.14-venv -y
     sudo apt install tree
  ```
  - Make it executable with `chmod +x init.sh`
  - Run it with `bash init.sh`
  - Confirm everything worked by executing `tree` and verifying you see the `init.sh` script

2) Create a Reproducable Virtual Machine

   - Create a file called "makefile"
     `nano makefile`
   - Add the follwing to the file:
     ```bash
     default:
       @cat makefile

      env:
        python3 -m venv env; . env/bin/activate; pip install --upgrade pip

      update:  env
        . env/bin/activate; pip install -r requirements.txt`
      ```

  - Test the file with the `make` command. This should echo the file contents back to you.
  - Create the "requirements.txt" file to add the required packages
    `nano requirements.txt`
  - Add the conents to the file:
    ```
    pandas
    numpy
    ```
  - Run the `make update` command
  - verify the environment is set up by executing `. env/bin/activate` followed by `pip list` and confirm the packages are shown
  - execute `deactivate` to leave the virtual environment

Step #2: Clone the Repo and push the updates
1) Setup the Github Credentials
  - create a file called "init_git_creds.sh"
    `nano init_git_creds.sh`
  - Add the following to the file:
    ```bash
    #!/usr/bin/bash

    USER=<your github email>
    NAME=<your github user name>
    
    git config --global --list
    
    git config --global user.email ${USER} 
    git config --global user.name  ${NAME} 
    
    git config --global --list
    ```
  - Make it executable with `chmod +x init_git_creds.sh`
  - Run it with `bash init_git_creds.sh`
  - Confirm your github email and username were echoed back to you

2) Clone the Repo
  - Make sure the Github repo exists
  - Execute `git clone git@github.com:<github user>/2508_DS5111_<uvaid>.git`
  - Change into the repo directory and create a new directory "scripts"
  - move the files you created into this new directory:
    `mv ~/init.sh .`
    `mv ~/init_git_creds.sh .`
    `mv ~/makefile .`
    `mv ~/requirements.txt .`

3) Push Updates to the Repo
  - `git add .`
  - `git commit -m "messsage"`
  - `git push`
  - `git log` will verify that the commit is complete 
