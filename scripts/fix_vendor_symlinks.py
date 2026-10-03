# -*- coding: utf-8 -*-
"""通用 vendor 死链修复器: 遍历内核树内指向 vendor/ 的悬空符号链接, 从 modules 仓补源。
用法: python3 fix_vendor_symlinks.py --tree common --modules modules
背景(mt6983 实测): OEM 清单把 vendor/ 源码放在独立仓, 内核树里的链接形如
  drivers/android/oplus_binder -> ../../../vendor/oplus/kernel/ipc
这些相对路径按 OEM 构建布局(kernel 与 vendor 仓并列)才成立, 裸 make -C common 必死链。
修法(对齐 209_mtk 死链替换): 取链接目标里 vendor/ 起的相对路径, 在 modules 仓找同名源,
用真实目录/文件替换链接本体。逻辑已按 mt6983@13.1 的 25 处死链全量验证。
"""
import os, sys, shutil

def main():
    args = sys.argv[1:]
    def opt(name, default):
        return args[args.index(name) + 1] if name in args else default
    tree = os.path.abspath(opt('--tree', 'common'))
    modules = os.path.abspath(opt('--modules', 'modules'))
    for d, n in ((tree, 'tree'), (modules, 'modules')):
        if not os.path.isdir(d):
            print(f'::error::{n} 目录不存在: {d} (cwd={os.getcwd()})')
            sys.exit(1)
    print(f'内核树: {tree}\nmodules 仓: {modules}')
    fixed, unresolved, ok_links = [], [], 0
    for root, dirs, files in os.walk(tree):
        for name in dirs + files:
            p = os.path.join(root, name)
            if not os.path.islink(p):
                continue
            tgt = os.readlink(p)
            # 1) 链接目标若在树内自洽, 不动
            res = os.path.normpath(os.path.join(os.path.dirname(p), tgt))
            if os.path.lexists(res):
                ok_links += 1
                continue
            # 2) 死链且目标含 vendor/: 按 vendor/ 起的路径到 modules 仓找源
            if 'vendor/' in tgt:
                rel = tgt[tgt.index('vendor/'):]
                src = os.path.join(modules, rel)
                if os.path.isdir(src) and not os.path.islink(src):
                    os.unlink(p)
                    os.makedirs(os.path.dirname(p), exist_ok=True)
                    shutil.copytree(src, p, symlinks=True)
                    fixed.append(rel)
                    continue
                if os.path.isfile(src):
                    os.unlink(p)
                    shutil.copyfile(src, p)
                    fixed.append(rel)
                    continue
            if p.replace(os.sep, '/').startswith('Documentation/'):
                print(f'  [skip-doc] {p} -> {tgt} (Documentation 树装饰, 构建不依赖)')
                continue
            unresolved.append((p, tgt))
    print(f'自洽链接: {ok_links} | 已补源: {len(fixed)} | 仍死链: {len(unresolved)}')
    for rel in fixed:
        print(f'  [fixed] {rel}')
    for p, tgt in unresolved:
        print(f'  [STILL-DANGLING] {p} -> {tgt}')
    if unresolved:
        print(f'::error::仍有 {len(unresolved)} 个死链无法补源')
        sys.exit(1)
    print('vendor 死链修复完成')

if __name__ == '__main__':
    main()
