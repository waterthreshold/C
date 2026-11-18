# Firmware Upgrade Wrapper (`ProdFWupgrade`)

## Purpose
A standardized wrapper script designed to simplify complex firmware upgrade arguments and eliminate clutter from messy file management.

---

## Installation

### Client Side
Run the automated setup script in your PowerShell environment:
```powershell
./setup.ps1
```

### Server Side
Copy the following required files to the target server environment:
* `PartitionUploadClt.exe`
* `ProdFW.json`
* Latest target firmware package

---

## Usage

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `-ip <string>` | Optional | Specifies a custom target IP address. |
| `-fw_path <string>` | Optional | Specifies the path to a specific firmware package. |
| `-httpsupport` | Optional | Triggers the DUT to launch the server via the HTTP protocol. |
| `-model <XX\|oo>` | **Required** | Project name (exclusive with `-listdevice`). |
| `-config_path <string>` | Optional | Path to the configuration file (default is `DeviceDeploy.json`). |
| `-listdevice` | Optional | Lists all supported devices. |
| `-ssh` | Optional | Triggers the DUT to launch the server via the SSH protocol. |

---
### example
```
ProdFWupgrade.ps1 -model deneb2 -ssh
```

## Configuration

### Server-Side (`ProdFW.json`)
* `clt_ver`: Expected client tool version (**Required**).
* `fw_name`: Target firmware filename (**Required**).

### Client-Side (`DeviceDeploy.json`)
* **Server Settings:**
  * `url`: Remote server URL (**Required**).
  * `protocol`: Remote server protocol, preferably FTP (**Required**).
  * `username`: Authentication username.
  * `password`: Authentication password.
* **Project Settings (per project name):**
  * `path`: Remote URL path.
  * `default_ip`: Factory static IP.
  * `parameter`: Additional reference Arguments.

---

## Test
Testing n time(s) upgrade

### example  
``` poweshell
./test100.ps1 -model larnaca2 -count 10
```

## Tool Options & Arguments

```text
-C,  --crc                  Do CRC verification after upload.
-d,  --dump-env             Dumps the update environment image into a file.
-b,  --prog-b-slot          Programmes slot B in eMMC.
-I <string>,  --identification <string>
                            (Required) Identification of device, used to differentiate different 
                            DOL settings when SAP numbers are not unique. Set to 'auto' if SAP 
                            code is 'auto', or leave empty if none.
-s <string>,  --sap <string>
                            (Required) SAP code for desired product. Set to 'auto' to read SAP code from EEPROM.
-z <string>,  --zip <string>
                            (Required) Zip archive containing firmware files.
-v,  --verbose              Detailed debug printout.
-c,  --clean                Clean end of partition.
-E <string>,  --erase-partition <string>
                            Erase specified partition (can be accepted multiple times; lower case; time-consuming!).
-e,  --erase                Erase partitions not having flash files (time-consuming!).
-f <string>,  --eeprom-file <string>
                            Configuration EEPROM file on camera for storing device information. 
                            Defaults to: /sys/devices/platform/e4000000.n_apb/e400a000.i2c/i2c-2/2-0054/eeprom.
-p <string>,  --partition-file <string>
                            File for partition table, typically ptb_meta.txt.
-i <string>,  --ip-addr <string>
                            (Required) IP address for the camera.
```