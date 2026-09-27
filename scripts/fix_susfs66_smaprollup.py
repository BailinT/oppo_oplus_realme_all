# -*- coding: utf-8 -*-
# SUS_MAP 手工移植: susfs 补丁 task_mmu.c Hunk#6(show_smaps_rollup SUS_MAP 包裹)在
# sm8750/mt6991 树上上下文失配打不上 -> 此脚本按树内现场手工包裹, 成功后移除对应 .rej
import os, re
root = './' if os.path.isdir('./fs/proc') else './common/'
p = root + 'fs/proc/task_mmu.c'
if not os.path.exists(p):
    print('skip: task_mmu.c not found at', p); raise SystemExit
src = open(p, encoding='utf-8', errors='ignore').read()
if 'CONFIG_KSU_SUSFS_SUS_MAP' in src:
    print('SUS_MAP wrapper already present, skip'); raise SystemExit
pat = re.compile(r'(/\* Case 4 above \*/\n(\t+)if \(vma->vm_end > last_vma_end\) \{\n)(\t+smap_gather_stats\(vma, &mss, last_vma_end\);\n\t+last_vma_end = vma->vm_end;\n)(\t+\})')
m = pat.search(src)
if not m:
    print('WARN: Case-4 block not found, .rej 保留待人工审查'); raise SystemExit
repl = (m.group(1)
    + m.group(2) + '#ifdef CONFIG_KSU_SUSFS_SUS_MAP\n'
    + m.group(2) + 'if (!vma->vm_file || !(SUSFS_IS_INODE_SUS_MAP(file_inode(vma->vm_file)))) {\n'
    + m.group(2) + '\tsmap_gather_stats(vma, &mss, last_vma_end);\n'
    + m.group(2) + '\tlast_vma_end = vma->vm_end;\n'
    + m.group(2) + '}\n'
    + m.group(2) + '#else\n'
    + m.group(3)
    + m.group(2) + '#endif /* CONFIG_KSU_SUSFS_SUS_MAP */\n'
    + m.group(4))
open(p, 'w', encoding='utf-8', newline='').write(src[:m.start()] + repl + src[m.end():])
print('SUS_MAP wrapper hand-ported into show_smaps_rollup')
rej = root + 'fs/proc/task_mmu.c.rej'
if os.path.exists(rej):
    os.remove(rej)
    print('removed', rej)
