#!/bin/bash

[ $(whoami) != "root" ] && echo "Requires Root!" && exit
export DEBIAN_FRONTEND=noninteractive

echo "Install common windows forensic parsers. Tested on Ubuntu 22.04.5 (included WSL-version)"
echo "Update and install basic utils..."
apt update
apt install -y curl wget git zip unzip p7zip-full gcc g++ build-essential python3-evtx apt-transport-https zlib1g

echo "Install Python3 and PIP..."
apt install -y python3 python3-pip 

echo "Install Powershell..."
source /etc/os-release
wget -q https://packages.microsoft.com/config/ubuntu/$VERSION_ID/packages-microsoft-prod.deb
dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb
echo "Package: dotnet* aspnet* netstandard*" > /etc/apt/preferences.d/dotnet_mix
echo "Pin: origin \"packages.microsoft.com\"" >> /etc/apt/preferences.d/dotnet_mix
echo "Pin-Priority: -10" >> /etc/apt/preferences.d/dotnet_mix
apt update
apt install -y powershell

#dotnet9
echo "Install dotnet runtime..."
add-apt-repository -y ppa:dotnet/backports
apt update
apt install -y dotnet-sdk-9.0 dotnet-runtime-9.0

echo "Install ZimmermanTools..."
wget https://download.ericzimmermanstools.com/Get-ZimmermanTools.zip -O /tmp/Get-ZimmermanTools.zip
mkdir /opt/eztool
unzip -o /tmp/Get-ZimmermanTools.zip -d /opt/eztool
rm /tmp/Get-ZimmermanTools.zip
pwsh /opt/eztool/Get-ZimmermanTools.ps1 -Dest /opt/eztool -NetVersion 9
base_dir="/opt/eztool"
find "$base_dir" -type f -name "*.dll" | while read -r dll_path; do
    folder=$(dirname "$dll_path")
    base_name=$(basename "$dll_path" .dll)
    echo "${folder}/${base_name}.exe"
    if [ -f "${folder}/${base_name}.exe" ]; then
        sh_file="${folder}/${base_name}"
        echo '#!/bin/bash' > "$sh_file"
        echo "dotnet \"$dll_path\" \"\$@\"" >> "$sh_file"
        chmod +x "$sh_file"
        mv "$sh_file" "/usr/local/bin/"
    fi
done

echo "Build and fix SQLECmd..."
sqlecmd_src="/opt/eztool/SQLECmd"
git clone https://github.com/EricZimmerman/SQLECmd "$sqlecmd_src"
bash -c "cd \"$sqlecmd_src\" && dotnet publish -f net9.0 -r linux-x64"
cp -rf "$sqlecmd_src/SQLMap/Maps" "$sqlecmd_src/SQLECmd/bin/Release/net9.0/linux-x64/publish"
ln -sf "$sqlecmd_src/SQLECmd/bin/Release/net9.0/linux-x64/publish/SQLECmd" /usr/local/bin/SQLECmd

echo "Install hayabusa..."
hayabusa_url="https://api.github.com/repos/Yamato-Security/hayabusa/releases/latest"
response=$(curl -s "$hayabusa_url")
latest_tag=$(echo "$response" | grep -oP '"tag_name":\s*"\K(.*?)(?=")')
hayabusa_zip="hayabusa-${latest_tag#v}-all-platforms.zip"
download_url=$(echo "$response" | grep -oP '"browser_download_url":\s*"\K[^"]*' | grep "$hayabusa_zip")
echo "Downloading $hayabusa_zip from $download_url"
curl -L -o "$hayabusa_zip" "$download_url"
hayabusa_target_dir="/opt/hayabusa"
unzip $hayabusa_zip -d $hayabusa_target_dir
rm "$hayabusa_zip"
hayabusa_binary_name="hayabusa-${latest_tag#v}-lin-x64-musl"
hayabusa_binary_path="$hayabusa_target_dir/$hayabusa_binary_name"
if [ -f "$hayabusa_binary_path" ]; then
    echo "Linking $hayabusa_binary_name to /usr/local/bin/hayabusa..."
    chmod +x "$hayabusa_binary_path"
    ln -sf "$hayabusa_binary_path" /usr/local/bin/hayabusa
fi

echo "Install chainsaw (required glibc >= 2.32)..."
chainsaw_api_url="https://api.github.com/repos/WithSecureLabs/chainsaw/releases/latest"
chainsaw_zip_name_encoded="chainsaw_all_platforms%2Brules.zip"
chainsaw_binary_name="chainsaw_x86_64-unknown-linux-gnu"
chainsaw_symlink="/usr/local/bin/chainsaw"
chainsaw_target_dir="/opt/chainsaw"
chainsaw_response=$(curl -s "$chainsaw_api_url")
chainsaw_latest_tag=$(echo "$chainsaw_response" | grep -oP '"tag_name":\s*"\K(.*?)(?=")')
chainsaw_download_url=$(echo "$chainsaw_response" | grep -oP '"browser_download_url":\s*"\K[^"]*' | grep "$chainsaw_zip_name_encoded")
wget -q -O "$chainsaw_zip_name_encoded" "$chainsaw_download_url"
mkdir -p "$chainsaw_target_dir"
unzip -o "$chainsaw_zip_name_encoded" -d "/opt"
rm "$chainsaw_zip_name_encoded"
chainsaw_binary_path="$chainsaw_target_dir/$chainsaw_binary_name"
ln -sf "$chainsaw_binary_path" "$chainsaw_symlink"
chmod +x "$chainsaw_binary_path"

echo "Install Zircolite..."
zircolite_bin="/usr/local/bin/zircolite"
git clone https://github.com/wagga40/Zircolite /opt/Zircolite
pip3 install -r /opt/Zircolite/requirements.full.txt
echo '#!/bin/bash' > "$zircolite_bin"
echo "python3 \"/opt/Zircolite/zircolite.py\" \"\$@\"" >> "$zircolite_bin"
chmod +x "$zircolite_bin"

echo "Install prefetchruncounts..."
apt install -y python3-libscca libscca1
prefetchruncounts_bin="/usr/local/bin/prefetchruncounts"
curl -L -o /opt/prefetchruncounts.py https://raw.githubusercontent.com/dfir-scripts/prefetchruncounts/refs/heads/master/prefetchruncounts.py
echo '#!/bin/bash' > "$prefetchruncounts_bin"
echo "python3 \"/opt/prefetchruncounts.py\" \"\$@\"" >> "$prefetchruncounts_bin"
chmod +x "$prefetchruncounts_bin"

echo "Install PowerShellScriptBlockExtractor..."
curl -L -o /opt/script_block_extract.py https://raw.githubusercontent.com/sweesiahh/PowerShellScriptBlockExtractor/refs/heads/main/script_block_extract.py
script_block_extract_bin="/usr/local/bin/script_block_extract"
echo '#!/bin/bash' > "$script_block_extract_bin"
echo "python3 \"/opt/script_block_extract.py\" \"\$@\"" >> "$script_block_extract_bin"
chmod +x "$script_block_extract_bin"




