import os
import shutil
import zipfile
from stuffs.general import General
from tools.helper import host
from tools.logger import Logger


class MicroG(General):
    partition = "system"
    dl_links = {
        "Standard": [
            "https://github.com/ayasa520/MinMicroG/releases/download/latest/MinMicroG-Standard-2.11.1-20230429100529.zip",
            "0fe332a9caa3fbb294f2e2b50f720c6b"
        ],
        "NoGoolag": [
            "https://github.com/ayasa520/MinMicroG/releases/download/latest/MinMicroG-NoGoolag-2.11.1-20230429100545.zip",
            "ff920f33f4c874eeae4c0444be427c68"
        ],
        "UNLP": [
            "https://github.com/ayasa520/MinMicroG/releases/download/latest/MinMicroG-UNLP-2.11.1-20230429100555.zip",
            "6136b383153c2a6797d14fb4d7ca3f97"
        ],
        "Minimal": [
            "https://github.com/ayasa520/MinMicroG/releases/download/latest/MinMicroG-Minimal-2.11.1-20230429100521.zip"
            "afb87eb64e7749cfd72c4760d85849da"
        ],
        "MinimalIAP": [
            "https://github.com/ayasa520/MinMicroG/releases/download/latest/MinMicroG-MinimalIAP-2.11.1-20230429100556.zip"
            "cc071f4f776cbc16c4c1f707aff1f7fa"
        ]
    }
    dl_link = ...
    act_md5 = ...
    dl_file_name = ...
    sdk = ...
    extract_to = "/tmp/microg/extract"
    copy_dir = "/var/lib/waydroid/overlay_rw/system"
    arch = host()
    rc_content = '''
on property:sys.boot_completed=1
    start microg_service

service microg_service /system/bin/sh /system/bin/npem
    user root
    group root
    oneshot
    '''
    files = [
        "priv-app/GoogleBackupTransport",
        "priv-app/MicroGUNLP",
        "priv-app/MicroGGMSCore",
        "priv-app/MicroGGMSCore/lib/x86_64/libmapbox-gl.so",
        "priv-app/MicroGGMSCore/lib/x86_64/libconscrypt_gmscore_jni.so",
        "priv-app/MicroGGMSCore/lib/x86_64/libcronet.102.0.5005.125.so",
        "priv-app/PatchPhonesky",
        "priv-app/PatchPhonesky/lib/x86_64/libempty_x86_64.so",
        "priv-app/AuroraServices",
        "bin/npem",
        "app/GoogleCalendarSyncAdapter",
        "app/NominatimNLPBackend",
        "app/MicroGGSFProxy",
        "app/LocalGSMNLPBackend",
        "app/DejaVuNLPBackend",
        "app/MozillaUnifiedNLPBackend",
        "app/AppleNLPBackend",
        "app/AuroraDroid",
        "app/LocalWiFiNLPBackend",
        "app/GoogleContactsSyncAdapter",
        "app/MicroGGSFProxy/MicroGGSFProxy",
        "framework/com.google.widevine.software.drm.jar",
        "framework/com.google.android.media.effects.jar",
        "framework/com.google.android.maps.jar",
        "lib64/libjni_keyboarddecoder.so",
        "lib64/libjni_latinimegoogle.so",
        "etc/default-permissions/microg-permissions.xml",
        "etc/default-permissions/microg-permissions-unlp.xml",
        "etc/default-permissions/gsync.xml",
        "etc/sysconfig/nogoolag.xml",
        "etc/sysconfig/nogoolag-unlp.xml",
        "etc/init/microg.rc",
        "etc/permissions/com.google.android.backuptransport.xml",
        "etc/permissions/com.android.vending.xml",
        "etc/permissions/com.google.android.gms.xml",
        "etc/permissions/com.aurora.services.xml",
        "etc/permissions/com.google.android.maps.xml",
        "etc/permissions/com.google.widevine.software.drm.xml",
        "etc/permissions/com.google.android.media.effects.xml",
        "lib/libjni_keyboarddecoder.so",
        "lib/libjni_latinimegoogle.so",
    ]

    def __init__(self, android_version="11", variant="Standard") -> None:
        super().__init__()
        self.dl_link = self.dl_links[variant][0]
        self.act_md5 = self.dl_links[variant][1]
        self.dl_file_name = f'MinMicroG-{variant}.zip'
        if android_version == "11":
            self.sdk = 30
        elif android_version == "13":
            self.sdk = 33

    def set_permissions(self, path):
        if "bin" in path.split("/"):
            perms = [0, 2000, 0o755, 0o777]
        else:
            perms = [0, 0, 0o755, 0o644]

        mode = os.stat(path).st_mode

        if os.path.isdir(path):
            mode |= perms[2]
        else:
            mode |= perms[3]

        os.chown(path, perms[0], perms[1])

        os.chmod(path, mode)

    def copy(self):

        Logger.info("Copying libs and apks...")
        dst_dir = os.path.join(self.copy_dir, self.partition)
        src_dir = os.path.join(self.extract_to, "system")
        if "arm" in self.arch[0]:
            sub_arch = "arm"
        else:
            sub_arch = "x86"
        if 64 == self.arch[1]:
            arch = f"{sub_arch}{'' if sub_arch=='arm' else '_'}64"
        for root, dirs, files in os.walk(src_dir):
            flag = False
            dir_name = os.path.basename(root)
            # 遍历文件
            if dir_name.startswith('-') and dir_name.endswith('-'):
                archs, sdks = [], []
                for i in dir_name.split("-"):
                    if i.isdigit():
                        sdks.append(i)
                    elif i:
                        archs.append(i)
                if len(archs) != 0 and arch not in archs and sub_arch not in archs or len(sdks) != 0 and str(self.sdk) not in sdks:
                    continue
                else:
                    flag = True

            for file in files:
                src_file_path = os.path.join(root, file)
                self.set_permissions(src_file_path)
                if not flag:
                    dst_file_path = os.path.join(dst_dir, os.path.relpath(
                        src_file_path, src_dir))
                else:
                    dst_file_path = os.path.join(dst_dir, os.path.relpath(
                        os.path.join(os.path.dirname(root), file), src_dir))
                if not os.path.exists(os.path.dirname(dst_file_path)):
                    os.makedirs(os.path.dirname(dst_file_path))
                # Logger.info(f"{src_file_path} -> {dst_file_path}")
                shutil.copy2(src_file_path, dst_file_path)
                if os.path.splitext(dst_file_path)[1].lower() == ".apk":
                    lib_dest_dir = os.path.dirname(dst_file_path)
                    with zipfile.ZipFile(dst_file_path, "r") as apk:
                        for file_info in apk.infolist():
                            file_name = file_info.filename
                            file_path = os.path.join(lib_dest_dir, file_name)
                            if file_info.filename.startswith(f"lib/{self.arch[0]}/") and file_name.endswith(".so"):
                                os.makedirs(os.path.dirname(
                                    file_path), exist_ok=True)
                                with apk.open(file_info.filename) as src_file, open(file_path, "wb") as dest_file:
                                    # Logger.info(f"{src_file} -> {dest_file}")
                                    shutil.copyfileobj(src_file, dest_file)

        rc_dir = os.path.join(dst_dir, "etc/init/microg.rc")
        if not os.path.exists(os.path.dirname(rc_dir)):
            os.makedirs(os.path.dirname(rc_dir))
        with open(rc_dir, "w") as f:
            f.write(self.rc_content)
        self.set_permissions(rc_dir)
