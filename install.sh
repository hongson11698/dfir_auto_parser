SCRIPT=$(readlink -f "$0")
BASEDIR="$(dirname "$SCRIPT")"

# for windows
chmod +x "$BASEDIR/installer/windows_parsers_installer.sh"
bash -c "$BASEDIR/installer/windows_parsers_installer.sh"

# for linux