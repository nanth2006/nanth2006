"""Rebuild every generated asset:  python tools/build_all.py   (needs: pip install fonttools)"""
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import banner, lanyard
banner.main()
open(os.path.join(banner.ROOT, 'lanyard.svg'), 'w').write(lanyard.build())
print('lanyard.svg')
subprocess.check_call([sys.executable, os.path.join(banner.ROOT, 'scripts', 'generate_cards.py'), '--offline'])
