#!/bin/bash
# ------------------------------------------------------
# One-Click Mr.Robot Lab Deployment for Proxmox VE
# Kali + Metasploitable2 + Monitor (Suricata, Fail2ban, DVWA, JuiceShop)
# Author: TryToNotTry
# ------------------------------------------------------

# === Настройки сети ===
BRIDGE="vmbr1"
NETWORK="192.168.56"
GATEWAY="${NETWORK}.1"

# === VM параметры ===
STORAGE="local-lvm"
VMID_KALI=9001
VMID_META=9002
VMID_MONITOR=9003

# === Проверка root ===
if [[ $EUID -ne 0 ]]; then
   echo "❌ Запусти скрипт от root!" 
   exit 1
fi

echo "🔧 Создаём bridge $BRIDGE..."
if ! grep -q "$BRIDGE" /etc/network/interfaces; then
cat <<EOF >> /etc/network/interfaces

auto $BRIDGE
iface $BRIDGE inet static
    address $GATEWAY/24
    bridge-ports none
    bridge-stp off
    bridge-fd 0
EOF
ifup $BRIDGE
fi

# === Скачивание образов ===
cd /tmp

echo "⬇️ Скачиваем Kali Linux cloud image..."
wget -q https://cdimage.kali.org/kali-2023.4/kali-linux-2023.4-cloud-amd64.qcow2 -O kali.qcow2

echo "⬇️ Скачиваем Metasploitable2..."
wget -q https://sourceforge.net/projects/metasploitable/files/Metasploitable2/Metasploitable2-Linux.zip -O metasploitable2.zip
unzip metasploitable2.zip
mv Metasploitable2-Linux.vmdk metasploitable2.vmdk
qemu-img convert -O qcow2 metasploitable2.vmdk metasploitable2.qcow2

echo "⬇️ Скачиваем Ubuntu cloud image (для Monitor)..."
wget -q https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img -O ubuntu.qcow2

# === Импорт в Proxmox ===
echo "📦 Импортируем образы в хранилище $STORAGE..."
qm create $VMID_KALI --name "Kali" --memory 4096 --cores 2 --net0 virtio,bridge=$BRIDGE
qm importdisk $VMID_KALI kali.qcow2 $STORAGE
qm set $VMID_KALI --scsihw virtio-scsi-pci --scsi0 $STORAGE:vm-$VMID_KALI-disk-0 --boot c --bootdisk scsi0 --ipconfig0 ip=${NETWORK}.10/24,gw=$GATEWAY

qm create $VMID_META --name "Metasploitable2" --memory 2048 --cores 2 --net0 virtio,bridge=$BRIDGE
qm importdisk $VMID_META metasploitable2.qcow2 $STORAGE
qm set $VMID_META --scsihw virtio-scsi-pci --scsi0 $STORAGE:vm-$VMID_META-disk-0 --boot c --bootdisk scsi0 --ipconfig0 ip=${NETWORK}.20/24,gw=$GATEWAY

qm create $VMID_MONITOR --name "Monitor" --memory 4096 --cores 2 --net0 virtio,bridge=$BRIDGE
qm importdisk $VMID_MONITOR ubuntu.qcow2 $STORAGE
qm set $VMID_MONITOR --scsihw virtio-scsi-pci --scsi0 $STORAGE:vm-$VMID_MONITOR-disk-0 --boot c --bootdisk scsi0 --ipconfig0 ip=${NETWORK}.40/24,gw=$GATEWAY

# === Cloud-init user-data ===
echo "📦 Настраиваем cloud-init для Monitor VM..."
cat <<EOF > user-data
#cloud-config
package_update: true
packages:
  - docker.io
  - docker-compose
  - suricata
  - fail2ban
runcmd:
  - [ sh, -c, "systemctl enable suricata --now" ]
  - [ sh, -c, "systemctl enable fail2ban --now" ]
  - [ sh, -c, "mkdir -p /opt/lab && cd /opt/lab && curl -o docker-compose.yaml https://raw.githubusercontent.com/Trytonottry/cyber-notes/proxmox-lab/main/docker-compose.yaml && docker-compose up -d" ]
EOF

cloud-localds monitor-seed.img user-data
qm set $VMID_MONITOR --ide2 $STORAGE:cloudinit
qm set $VMID_MONITOR --serial0 socket --boot c --bootdisk scsi0

# === Запуск VM ===
echo "🚀 Запускаем виртуалки..."
qm start $VMID_KALI
qm start $VMID_META
qm start $VMID_MONITOR

echo "✅ Лаборатория готова!"
echo "   Kali: ${NETWORK}.10"
echo "   Metasploitable2: ${NETWORK}.20"
echo "   Monitor (Suricata + Fail2ban + Docker apps): ${NETWORK}.40"
echo "   DVWA: http://${NETWORK}.40:80"
echo "   Juice Shop: http://${NETWORK}.40:3000"
