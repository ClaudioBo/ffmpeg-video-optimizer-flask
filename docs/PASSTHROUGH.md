# Hacer passthrough de la iGPU de AMD Ryzen al contenedor LXC
Se tendra que configurar Proxmox para que este disponible la grafica a nivel host de Proxmox, y poderla "passthroughear" a uno o varios contenedores LXC.  
Esta guia es para mi **`Beelink SER5 MAX`** que tiene una **`AMD Ryzen 7 5800H`**  
Esta guia esta completamente untested ya que es un recopilatorio sacado de millones de comandos innecesarios que puse :)  

## Configurar BIOS para habilitar la iGPU para Proxmox
1. Meterse a la BIOS
2. Cambiar **`Advanced -> SVM`** a **`Enabled`**
3. Cambiar **`IOMMU`** a **`Enabled`**
4. Opcionalmente: Cambiar **`UMA Frame Buffer Size`** a **`4G`** o lo que desees, esta es la VRAM
5. **`Save and Exit`**

## Configurar Proxmox para que tenga la iGPU disponible
1. Editar **`nano /etc/default/grub`** y cambiar el valor de **`GRUB_CMDLINE_LINUX_DEFAULT`** por:
    ```yaml
    GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_iommu=on iommu=pt"
    ```
2. Comentar **todo** de **`nano /etc/modprobe.d/vfio.conf`**
3. Comentar **todo** de **`nano /etc/modprobe.d/blacklist-amdgpu.conf`**
4. Comentar **todo** de **`nano /etc/modules`** y agregar al final
    ```
    drm
    amdgpu
    ```
5. Actualizar **`grub`** y **`initramfs`**, y reiniciar el servidor
    ```sh
    update-grub
    update-initramfs -u -k all
    reboot now
    ```
6. **`ls -l /dev/dri`** para comprobar que exista el archivo **`renderD128`**
7. **`nano /etc/pve/lxc/101.conf`**
    ```yaml
    lxc.cgroup2.devices.allow: c 226:128 rwm
    lxc.mount.entry: /dev/dri/renderD128 dev/dri/renderD128 none bind,create=file
    ```
8. Iniciar contenedor LXC y correr **`ls -l /dev/dri/`** para comprobar que exista el archivo **`renderD128`**