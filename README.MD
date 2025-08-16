# **DFIRAutoParser**  
Automated execution of multiple forensic artifact parsers, inspired by the modular approach of Kape-Modules. 
Support for both Windows and (soon) Linux artifacts.

## Features
- ✅ Automatically downloads and sets up supported parsers (Tested on Ubuntu 22.04.5)
- ✅ Works with common artifacts collected using tools like KAPE, CDIR, and other live acquisition solutions
- ✅ Integration with many of Eric Zimmerman's forensic tools, included Hayabusa, Chainsaw, Zircolite,...
- ✅ Included config file to define which parsers to run
- ✅ Run individual parsers for quick analysis or pivoting in investigations

## TODO
- [ ] Support other necessary artifacts on Windows
- [ ] Support Linux artifacts collected using common Linux forensic tools

## Instructions

```bash
# Installer
git clone https://github.com/hongson11698/dfir_auto_parser.git
cd dfir_auto_parser
sudo ./install.sh

# Usage
___Available parsers___
module_AmcacheParser
module_AppCompatCacheParser
module_EvtxECmd
module_JLECmd
module_MFTECmd
module_PECmd
module_RBCmd
module_RECmd
module_RECmd_ASEP
module_RecentFileCacheParser
module_SBECmd
module_SQLECmd
module_WxTCmd
module_chainsaw
module_hayabusa_logon
module_hayabusa_timeline
module_prefetchruncounts
module_script_block_powershell
module_zircolite
_______________________
usage: windows_parser.py [-h] (-s S | -r R) [-f F] [-m M]

options:
  -h, --help  show this help message and exit
  -s S        single_target_folder
  -r R        multiple_target_folders
  -f F        target_file_patterns (regex, default from target.txt)
  -m M        single_parser
```

# Others works
- https://ericzimmerman.github.io/#!index.md
- https://github.com/Yamato-Security/hayabusa
- https://github.com/WithSecureLabs/chainsaw
- https://github.com/wagga40/Zircolite
- https://github.com/CyberDefenseInstitute/CDIR
- https://github.com/Tadjmen/CLLF
- https://github.com/WithSecureLabs/LinuxCatScale
- https://github.com/tclahr/uac