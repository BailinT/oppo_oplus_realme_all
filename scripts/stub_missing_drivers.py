# -*- coding: utf-8 -*-
# 通用清障: 原厂配置启用的内建驱动在公开树缺源码目录(死链) -> 建空 Makefile stub 让 make 跳过
# 用法: python3 stub_missing_drivers.py (在 kernel_workspace 下运行, 读 out/.config)
import os, re

cfg = {}
for line in open('out/.config', encoding='utf-8', errors='ignore'):
    m = re.match(r'(CONFIG_[A-Z0-9_]+)=(y|m)', line)
    if m:
        cfg[m.group(1)] = m.group(2)

pat = re.compile(r'obj-\$\(CONFIG_([A-Za-z0-9_]+)\)\s*\+?=\s*([A-Za-z0-9_./-]+)/')
stubbed = 0
for top in ('drivers', 'sound', 'techpack'):
    base = os.path.join('./common', top)
    if not os.path.isdir(base):
        continue
    for dirpath, dirs, files in os.walk(base):
        if 'Makefile' not in files:
            continue
        for line in open(os.path.join(dirpath, 'Makefile'), encoding='utf-8', errors='ignore'):
            m = pat.search(line)
            if not m:
                continue
            c, d = m.group(1), m.group(2)
            full = os.path.join(dirpath, d)
            if os.path.isdir(full):
                continue
            if 'CONFIG_' + c not in cfg:
                continue
            os.makedirs(full, exist_ok=True)
            mf = os.path.join(full, 'Makefile')
            if not os.path.exists(mf):
                open(mf, 'w').write('# stub: source missing in public tree\n')
                stubbed += 1
                print('stub:', full, '(CONFIG_' + c + ')')
print('共 stub', stubbed, '个缺失驱动目录')
