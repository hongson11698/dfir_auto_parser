import argparse
from concurrent.futures import ThreadPoolExecutor
import inspect
from pathlib import Path
from datetime import datetime

import os
import re
import shlex
import sys
import subprocess
import tempfile
import threading
import time
import windows_config

ROOT_RESULT_PATH = "WindowsParser"
# need config for each system...

if sys.platform == "linux":
    AmcacheParser_bin = "AmcacheParser"
    AppCompatCacheParser_bin = "AppCompatCacheParser"
    PECmd_bin = "PECmd"
    prefetchruncounts_bin = "prefetchruncounts"

    JLECmd_bin = "JLECmd"
    RBCmd_bin = "RBCmd"
    SBECmd_bin = "SBECmd"
    WxTCmd_bin = "WxTCmd"
    RecentFileCacheParser_bin = "RecentFileCacheParser"
    RECmd_bin = "RECmd"
    SQLECmd_bin = "SQLECmd"
    MFTECmd_bin = "MFTECmd"

    EvtxEcmd_bin = "EvtxECmd" 
    hayabusa_bin = "hayabusa"
    chainsaw_bin = "chainsaw"
    zircolite_bin = "zircolite"
    script_block_bin = "script_block_extract"

    zircolite_evtx_bin = r"/opt/Zircolite/bin/evtx_dump_lin"
    eztool_dir = r"/opt/eztool/net9"
    hayabusa_dir = r"/opt/hayabusa"
    chainsaw_dir = r"/opt/chainsaw"
    zircolite_dir =  r"/opt/Zircolite"

    # wmi

elif sys.platform == "win32":
    AmcacheParser_bin = r"D:\Tools\Get-ZimmermanTools\AmcacheParser.exe"
    AppCompatCacheParser_bin = r"D:\Tools\Get-ZimmermanTools\AppCompatCacheParser.exe"
    PECmd_bin = r"D:\Tools\Get-ZimmermanTools\PECmd.exe"
    prefetchruncounts_bin = r"python3 'D:\Tools\Get-ZimmermanTools\prefetchruncounts.py'"
    JLECmd_bin = r"D:\Tools\Get-ZimmermanTools\JLECmd.exe"
    RBCmd_bin =  r"D:\Tools\Get-ZimmermanTools\RBCmd"

    SBECmd_bin = r"D:\Tools\Get-ZimmermanTools\SBECmd.exe"
    WxTCmd_bin = r"D:\Tools\Get-ZimmermanTools\WxTCmd.exe"
    RecentFileCacheParser_bin = r"D:\Tools\Get-ZimmermanTools\RecentFileCacheParser.exe"
    SQLECmd_bin = r"D:\Tools\Get-ZimmermanTools\SQLECmd.exe"
    MFTECmd_bin = r"D:\Tools\Get-ZimmermanTools\MFTECmd.exe"
    RECmd_bin = r"D:\Tools\Get-ZimmermanTools\RECmd\RECmd.exe"
    RECmd_dir = r"D:\Tools\Get-ZimmermanTools\RECmd"

    EvtxEcmd_bin = r"D:\Tools\Get-ZimmermanTools\EvtxEcmd.exe" 
    hayabusa_bin = r"D:\Tools\Get-ZimmermanTools\hayabusa.exe"
    chainsaw_bin = r"D:\Tools\Get-ZimmermanTools\chainsaw.exe"
    zircolite_bin = r"D:\Tools\Get-ZimmermanTools\zircolite.exe"
    script_block_bin = r"D:\Tools\Get-ZimmermanTools\script_block_bin.exe"

    eztool_dir = r"D:\Tools\Get-ZimmermanTools"
    hayabusa_dir = r"D:\Tools\hayabusa"
    chainsaw_dir = r"D:\Tools\chainsaw"
    zircolite_dir =  r"D:\Tools\zircolite"
    zircolite_evtx_bin = r"D:\Tools\Zircolite\bin\evtx_dump_win.exe"
      
    # wmi

processing_module = []

def run_and_get_output(args, working_dir):
    proc = subprocess.Popen(args, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output = "".join(proc.stdout.readlines())
    sts = proc.returncode
    if sts is None: sts = 0
    return sts, output

def execute_process(path, command, log_file, working_dir = tempfile.gettempdir()):
    if not log_file.exists():
        if ' ' in path:
            path = f"\"{path}\""
        args = [path] + shlex.split(command)
        status, output = run_and_get_output(args, working_dir)
        if status == 0:
            with open(log_file, "w") as f:
                f.write(output)    
        else:
            with open(str(log_file).replace(".txt", "_failed.txt"), "w") as f:
                f.write(f"Run '{path} {command}' failed!\r\n")   
                f.write(output)
    return

def module_script_block_powershell(source, dest, log_prefix):
    powershell_evtx = ""
    for file_evtx in Path(source).rglob(r"Microsoft-Windows-PowerShell%4Operational.evtx"):
        powershell_evtx = file_evtx.resolve()
        break
    if powershell_evtx != "":
        powershell_script_block_result_dir = Path(dest).joinpath("powershell_script_block")

        os.makedirs(powershell_script_block_result_dir, exist_ok=True)

        script_block_command = f"-e \"{powershell_evtx}\" -o {powershell_script_block_result_dir} -s"

        log_ps_script_block_file = powershell_script_block_result_dir.joinpath(f"output_{log_prefix}.txt")

        execute_process(script_block_bin, script_block_command, log_ps_script_block_file, hayabusa_dir)

def module_SQLECmd(source, dest, log_prefix):
    log_file = Path(dest).joinpath(f"output_{log_prefix}.txt")
    command_line = f"-d \"{source}\" --csv \"{dest}\""
    execute_process(SQLECmd_bin, command_line, log_file)
    return

def module_MFTECmd(source, dest, log_prefix):
    mft_file = ""
    j_file = ""

    for path in Path(source).rglob("*$MFT"):
        mft_file = path.resolve()
    for path in Path(source).rglob("*$J"):
        j_file = path.resolve()
    
    log_ntfs_file = Path(dest).joinpath(f"output_{log_prefix}_mft_j.txt")

    if mft_file != "" and j_file != "":
        command_line = f"-f \"{j_file}\" -m \"{mft_file}\" --csv \"{dest}\""
        execute_process(MFTECmd_bin, command_line, log_ntfs_file)
    elif mft_file != "":
        command_line = f"-f \"{mft_file}\" --csv \"{dest}\""
        execute_process(MFTECmd_bin, command_line, log_ntfs_file)
    return

def module_AmcacheParser(source, dest, log_prefix):
    log_file = Path(dest).joinpath(f"output_{log_prefix}.txt")
    for amcache_file_path in Path(source).rglob("Amcache.hve"):
        command_line = f"-f \"{amcache_file_path}\" --csv \"{dest}\" -i --mp"
        execute_process(AmcacheParser_bin, command_line, log_file)
        break
    return

def module_AppCompatCacheParser(source, dest, log_prefix):
    log_file = Path(dest).joinpath(f"output_{log_prefix}.txt")
    for appcom_file_path in Path(source).rglob("SYSTEM"):
        command_line = f"-f \"{appcom_file_path}\" --csv \"{dest}\""
        execute_process(AppCompatCacheParser_bin, command_line, log_file)
        break
    return

def module_prefetchruncounts(source, dest, log_prefix):
    log_file = Path(dest).joinpath(f"output_{log_prefix}.csv")
    prefetch_dir = ""
    for prefetch_search_dir in Path(source).rglob("*"):
        if prefetch_search_dir.name.lower() == "prefetch":
            prefetch_dir = prefetch_search_dir.resolve()
            break

    if prefetch_dir != "":
        command_line = f"\"{prefetch_dir}\""
        execute_process(prefetchruncounts_bin, command_line, log_file)
    return

def module_EvtxECmd(source, dest, log_prefix):
    evtxcmd_result_dir = Path(dest).joinpath("sofelk_evtx")
    os.makedirs(evtxcmd_result_dir, exist_ok=True)
    log_file = Path(evtxcmd_result_dir).joinpath(f"output_{log_prefix}.txt")
    command_line = f"-d \"{source}\" --json \"{evtxcmd_result_dir}\""
    execute_process(EvtxEcmd_bin, command_line, log_file)
    return

def module_PECmd(source, dest, log_prefix):
    log_file = Path(dest).joinpath(f"output_{log_prefix}.txt")
    command_line = f"-d \"{source}\" --csv \"{dest}\" --mp -q"
    execute_process(PECmd_bin, command_line, log_file)
    return

def module_JLECmd(source, dest, log_prefix):
    log_file = Path(dest).joinpath(f"output_{log_prefix}.txt")
    command_line = f"-d \"{source}\" --csv \"{dest}\" --mp -q"
    execute_process(JLECmd_bin, command_line, log_file)
    return

def module_RBCmd(source, dest, log_prefix):
    log_file = Path(dest).joinpath(f"output_{log_prefix}.txt")
    command_line = f"-d \"{source}\" --csv \"{dest}\" -q"
    execute_process(RBCmd_bin, command_line, log_file)
    return

def module_SBECmd(source, dest, log_prefix):
    log_file = Path(dest).joinpath(f"output_{log_prefix}.txt")
    command_line = f"-d \"{source}\" --csv \"{dest}\""
    execute_process(SBECmd_bin, command_line, log_file)
    return

def module_WxTCmd(source, dest, log_prefix):
    log_file = Path(dest).joinpath(f"output_{log_prefix}.txt")
    for activities_file_path in Path(source).rglob("ActivitiesCache.db"):
        command_line = f"-f \"{activities_file_path}\" --csv \"{dest}\""
        execute_process(AmcacheParser_bin, command_line, log_file)
        break
    return

def module_RecentFileCacheParser(source, dest, log_prefix):
    log_file = Path(dest).joinpath(f"output_{log_prefix}.txt")
    for recent_cache_file_path in Path(source).rglob("RecentFileCache.bcf"):
        command_line = f"-f \"{recent_cache_file_path}\" --csv \"{dest}\""
        execute_process(AmcacheParser_bin, command_line, log_file)
        break
    return

def module_RECmd_ASEP(source, dest, log_prefix):
    log_reg_asep_file = Path(dest).joinpath(f"output_{log_prefix}_reg_asep.txt")
    regsitry_asep_script = Path(eztool_dir).joinpath("RECmd", "BatchExamples", "RegistryASEPs.reb")
    command_line_RegistryASEP = f"-d \"{source}\" --bn \"{regsitry_asep_script}\" --nl false --csv \"{dest}\""
    execute_process(RECmd_bin, command_line_RegistryASEP, log_reg_asep_file)
    return

def module_RECmd(source, dest, log_prefix):
    log_dfir_batch_file = Path(dest).joinpath(f"output_{log_prefix}_dfir_batch.txt")
    dfir_batch_script = Path(eztool_dir).joinpath("RECmd", "BatchExamples", "DFIRBatch.reb")
    command_line_dfir_batch = f"-d \"{source}\" --bn \"{dfir_batch_script}\" --nl false --csv \"{dest}\""
    execute_process(RECmd_bin, command_line_dfir_batch, log_dfir_batch_file)
    
    return

def module_hayabusa_logon(source, dest, log_prefix):
    evtx_dir = None
    for sample_evtx in Path(source).rglob("*.evtx"):
        evtx_dir = sample_evtx.parent.resolve()
        break

    if evtx_dir == None or not evtx_dir.exists():
        return
    
    haya_result_dir = Path(dest).joinpath("hayabusa")

    os.makedirs(haya_result_dir, exist_ok=True)

    haya_result_logon = haya_result_dir.joinpath("logon-summary.csv")

    haya_logon_cmd = f'logon-summary -q --no-color -d "{evtx_dir}" -o "{haya_result_logon}"'

    log_logon_file = haya_result_dir.joinpath(f"output_{log_prefix}_logon.txt")

    execute_process(hayabusa_bin, haya_logon_cmd, log_logon_file, hayabusa_dir)
    
    return

def module_hayabusa_timeline(source, dest, log_prefix):
    evtx_dir = None
    for sample_evtx in Path(source).rglob("*.evtx"):
        evtx_dir = sample_evtx.parent.resolve()
        break

    if evtx_dir == None or not evtx_dir.exists():
        return
    
    haya_result_dir = Path(dest).joinpath("hayabusa")

    os.makedirs(haya_result_dir, exist_ok=True)

    haya_result_timeline = haya_result_dir.joinpath("timeline")

    haya_timeline_cmd = f'csv-timeline -q --no-color -w -T -H "{haya_result_timeline}_overview.html" -d "{evtx_dir}" -o "{haya_result_timeline}.csv"'

    log_timeline_file = haya_result_dir.joinpath(f"output_{log_prefix}_timeline.txt")
    
    execute_process(hayabusa_bin, haya_timeline_cmd, log_timeline_file, hayabusa_dir)

    return

def module_chainsaw(source, dest, log_prefix):
    evtx_dir = None
    for sample_evtx in Path(source).rglob("*.evtx"):
        evtx_dir = sample_evtx.parent.resolve()
        break

    if evtx_dir == None or not evtx_dir.exists():
        return
    
    chainsaw_result_dir = Path(dest).joinpath("chainsaw")

    chainsaw_rule_dir = Path(chainsaw_dir).joinpath("rules")
    chainsaw_sigma_dir = Path(chainsaw_dir).joinpath("sigma")
    chainsaw_mappings_file = Path(chainsaw_dir).joinpath("mappings", "sigma-event-logs-all.yml")

    os.makedirs(chainsaw_result_dir, exist_ok=True)

    chainsaw_command_line = f"hunt {evtx_dir} --rule \"{chainsaw_rule_dir}\" --sigma \"{chainsaw_sigma_dir}\" --mapping \"{chainsaw_mappings_file}\" --csv --output {chainsaw_result_dir} --full --skip-errors"

    log_chainsaw_file = chainsaw_result_dir.joinpath(f"output_{log_prefix}.txt")

    execute_process(chainsaw_bin, chainsaw_command_line, log_chainsaw_file, chainsaw_dir)

    return

def module_zircolite(source, dest, log_prefix):
    zircolite_config_file = Path(zircolite_dir).joinpath("config", "fieldMappings.json")

    zircolite_rule_windows_1 = Path(zircolite_dir).joinpath("rules", "rules_windows_generic_pysigma.json")

    os.makedirs(Path(dest).joinpath("zircolite"), exist_ok=True)

    zircolite_result_db_file = Path(dest).joinpath("zircolite", "Zircolite_detections.db")

    zircolite_result_json_file = Path(dest).joinpath("zircolite", "Zircolite_detections.json")

    evtx_dir = None
    for sample_evtx in Path(source).rglob("*.evtx"):
        evtx_dir = sample_evtx.parent.resolve()
        break

    if evtx_dir == None or not evtx_dir.exists():
        return
    zircolite_command_line = f"--events {evtx_dir} --ruleset \"{zircolite_rule_windows_1}\" --outfile \"{zircolite_result_json_file}\" --dbfile \"{zircolite_result_db_file}\" --config \"{zircolite_config_file}\" --evtx_dump \"{zircolite_evtx_bin}\""

    log_zircolite_file =  Path(dest).joinpath("zircolite", f"output_{log_prefix}.txt")

    execute_process(zircolite_bin, zircolite_command_line, log_zircolite_file, tempfile.gettempdir())

    return

def entry_processing(entry, module_function=None):
    global processing_module

    dest = Path(entry["full_path"]).joinpath(ROOT_RESULT_PATH)

    print("{0}: Destination directory set to {1}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), dest))

    if module_function == None:
        module_threads = []
        for module in processing_module:
            module_result_dir = Path.joinpath(dest, module["name"])
            os.makedirs(module_result_dir, exist_ok=True)
            for module_function in module["module_list"]:
                result_thread = threading.Thread(target=module_function, args=(entry["full_path"], module_result_dir, module_function.__name__))
                result_thread.name = module_function.__name__
                result_thread.start()
                module_threads.append(result_thread)
        total_module = len(module_threads)                
        finished_module = 0
        while module_threads:
            time.sleep(5)
            temp_active_threads = []
            for thread in module_threads:
                if thread.is_alive():
                    temp_active_threads.append(thread)
                else:
                    finished_module+=1
                    print("{0}: {1} finished ({2}/{3}).".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), thread.name, finished_module, total_module))
            module_threads = temp_active_threads
    else:
        module_result_dir = Path.joinpath(dest, module_function.__name__)
        module_function(entry["full_path"], module_result_dir, module_function.__name__)
    return

def windows_parser(target_dir, target_pattern_file = Path(__file__).parent.joinpath("target.txt"), module_function=None):  
    pattern_data = []

    with open(target_pattern_file, "r") as f:
        pattern_data += f.read().splitlines()

    print(f"using patterns from {target_pattern_file}")
    
    pattern_list = []
    for pattern in pattern_data:
        pattern = str(pattern).strip()
        if pattern == "":
            continue
        print(f"Found pattern: \"{pattern}\"")
        pattern_list.append(pattern)

    data_entry = []

    print("{0}: Parsing {1}...".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), target_dir))
    for path in Path(target_dir).rglob("*"):
        if path.is_dir():
            for pattern in pattern_list:
                if re.search(pattern, path.name):
                    data_entry.append({"full_path": str(path.resolve())})           
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = executor.map(entry_processing, data_entry, [module_function] * len(data_entry))
    
    print("{0}: Done...".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def init_module_config():   
    global processing_module
    
    event_module_config = [
        [windows_config.HayabusaLogonParser, module_hayabusa_logon],
        [windows_config.HayabusaTimelineParser, module_hayabusa_timeline],
        [windows_config.ChainsawParser, module_chainsaw], 
        [windows_config.EvtxEParser, module_EvtxECmd], 
        [windows_config.PSScriptBlockParser, module_script_block_powershell], 
        [windows_config.ZircoliteParser, module_zircolite]
    ]

    execution_module_config = [
        # [module, function]
        [windows_config.AmcacheParser, module_AmcacheParser], 
        [windows_config.AppCompatCacheParser,module_AppCompatCacheParser],
        [windows_config.PrefectParser, module_prefetchruncounts if sys.platform == "linux" else module_PECmd]
    ]

    ntfs_module_config = [
        (windows_config.MFTParser, module_MFTECmd)
    ]

    file_module_config = [
        [windows_config.JLEParser, module_JLECmd], 
        [windows_config.RBParser, module_RBCmd], 
        [windows_config.SBEParser, module_SBECmd], 
        [windows_config.WxTParser, module_WxTCmd], 
        [windows_config.RecentFileParser, module_RecentFileCacheParser]
    ]

    registry_module_config = [
        [windows_config.RegistryParser, module_RECmd],
        [windows_config.RegistryASEPParser, module_RECmd_ASEP]
    ]

    sqldata_module_config = [
        [windows_config.SQLDataParser, module_SQLECmd]
    ]

    processing_module = [
        {"name": "execution", "module_config": execution_module_config, "module_list": []},
        {"name": "ntfs", "module_config": ntfs_module_config, "module_list": []},
        {"name": "events", "module_config": event_module_config, "module_list": []},
        {"name": "file", "module_config": file_module_config, "module_list": []},
        {"name": "registry", "module_config": registry_module_config, "module_list": []},
        {"name": "sqldata", "module_config": sqldata_module_config, "module_list": []},
    ]

    modules = []
    for module in processing_module:
        for module_config in module["module_config"]:
            if module_config[0]:
                module_function = module_config[1]
                modules.append(module_function.__name__)
                module["module_list"].append(module_function)
    print("using {0} modules from config: \n\t{1}".format(len(modules), "\n\t".join(modules)))
    return

def list_module_parser():
    current_module = sys.modules[__name__]
    functions = {}
    for name, obj in inspect.getmembers(current_module):
        if inspect.isfunction(obj) and name.startswith("module_"):
            functions[name] = obj
    return functions

if __name__ == "__main__":
    print("___Available parsers___")
    functions = list_module_parser()
    for name in functions.keys():
        print(name)
    print("_______________________")

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-s", help="single_target_folder")
    group.add_argument("-r", help="multiple_target_folders")

    parser.add_argument("-f", help="target_file_patterns (regex, default from target.txt)")
    parser.add_argument("-m", help="single_parser")
    
    args = parser.parse_args()

    module_function = None
    if args.m:
        print(f"using single_module: {args.m}")
        if args.m in functions:
            module_function = functions[args.m]
        else:
            print(f"module not found!")
            exit(-1)
    else:
        init_module_config()

    if args.r:
        print("multiple_target_folder")
        multiple_target = Path(args.r)
        if not Path(multiple_target).exists():
            print(f"target not found!")
            exit(-1)
        if args.f:
            print("apply target_file_path")
            target_pattern = Path(args.f)
            windows_parser(multiple_target, target_pattern, module_function)
        else:
            windows_parser(multiple_target, module_function=module_function)
    
    elif args.s:
        print("single_target_folder")
        single_target = Path(args.s)
        if not Path(single_target).exists():
            print(f"target not found!")
            exit(-1)
        entry_processing({"name": single_target.name, "full_path": str(single_target.resolve())}, module_function)
   
    exit(0)