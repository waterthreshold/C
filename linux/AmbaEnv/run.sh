#!/bin/sh
docker run -it -v ${HOME}/AmbaEnv/run_script:/run_script -v ${HOME}/AmbaEnv/amba_fw:/amba_fw ambaenv
