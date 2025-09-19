import os
import sys
import subprocess
from logging import info

def detect_python_paths():
    python_include = os.path.join(os.path.dirname(sys.executable), "Include")
    python_lib = os.path.join(
        os.path.dirname(sys.executable),
        "libs",
        f"python{sys.version_info.major}{sys.version_info.minor}.lib"
    )
    if not os.path.exists(python_lib):
        raise FileNotFoundError(
            f"Cannot find {python_lib}. You need the static Python library for standalone EXE."
        )
    return python_include, python_lib

def find_vcvars():
    vswhere = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    result = subprocess.run([vswhere, "-latest", "-products", "*", "-requires",
                             "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                             "-property", "installationPath"],
                            capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        raise FileNotFoundError("Visual Studio installation not found via vswhere.")
    
    install_path = result.stdout.strip()
    vcvars = os.path.join(install_path, "VC", "Auxiliary", "Build", "vcvarsall.bat")
    if not os.path.exists(vcvars):
        raise FileNotFoundError(f"Cannot find vcvarsall.bat at {vcvars}")
    return vcvars

def run_in_dev_env(vcvars_path, cmd_list, arch="x64"):
    full_cmd = f'cmd /c "call \"{vcvars_path}\" {arch} && {" ".join(cmd_list)}"'
    subprocess.run(full_cmd, shell=True, check=True)

def generate_c_file(source_file, temp_c_file):
    info("Generating C file from Python...")
    subprocess.run([sys.executable, "-m", "cython", "--embed", "-3", source_file, "-o", temp_c_file], check=True)
    info(f"Generated {temp_c_file}")

def compile_exe(vcvars_path, temp_c_file, exe_file, python_include, python_lib, windowed=False):
    mode = "windowed" if windowed else "console"
    info(f"Compiling standalone EXE ({mode} mode, using x64 Developer Command Prompt)...")
    
    compile_command = [
        "cl",
        "/nologo",
        "/Ox",
        "/MD",
        f"/I{python_include}",
        temp_c_file,
        "/link",
        f"/OUT:{exe_file}",
        python_lib,
        "/NODEFAULTLIB:python3??.lib"
    ]
    
    if windowed:
        compile_command += ["/SUBSYSTEM:WINDOWS", "/ENTRY:mainCRTStartup"]
    
    run_in_dev_env(vcvars_path, compile_command)
    info(f"Standalone executable created at: {exe_file}")

def cleanup(temp_c_file, temp_build_dir):
    info("Cleaning up temporary files...")
    if os.path.exists(temp_c_file):
        os.remove(temp_c_file)
    for f in os.listdir("."):
        if f.endswith((".obj", ".pdb", ".lib", ".exp")):
            os.remove(f)
    if os.path.isdir(temp_build_dir) and not os.listdir(temp_build_dir):
        os.rmdir(temp_build_dir)
    info("EXE compilation completed.")

def main(source_file, windowed=False):
    temp_build_dir = os.path.abspath("build_temp")
    os.makedirs(temp_build_dir, exist_ok=True)

    temp_c_file = os.path.join(temp_build_dir, "temp_c_file.c")
    exe_file = os.path.abspath(os.path.splitext(os.path.basename(source_file))[0] + ".exe")

    vcvars_path = find_vcvars()
    python_include, python_lib = detect_python_paths()

    generate_c_file(source_file, temp_c_file)
    compile_exe(vcvars_path, temp_c_file, exe_file, python_include, python_lib, windowed)
    cleanup(temp_c_file, temp_build_dir)