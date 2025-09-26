import logging
from argparse import ArgumentParser
from components.compile import main as compile_main
from components.adddata import add_icon_to_executable, add_uac_to_executable

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def main():
    parser = ArgumentParser(description="Amoongoos - Compile Python scripts into standalone Windows executables.")
    parser.add_argument("source_file", help="Path to the Python source file to compile.")
    parser.add_argument("--uac", "-uac", action="store_true", help="Make the executable request UAC elevation.")
    parser.add_argument("--icon", "-i", help="Path to the icon file (.ico) to embed in the executable.")
    parser.add_argument("--windowed", "-w", action="store_true", help="Compile the executable in windowed mode (no console).")
    args = parser.parse_args()
    setup_logging()

    compile_main(args.source_file, args.windowed)
    if args.icon:
        add_icon_to_executable(args.source_file, args.icon, folder=False)
    if args.uac:
        add_uac_to_executable(args.source_file, folder=False)    

if __name__ == "__main__":
    main()        