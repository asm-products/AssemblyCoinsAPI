import node
import time

print node.access.getblockcount()

def load_block_file(blockn):
    file_path="/Users/barisser/Library/Application Support/Bitcoin/blocks/"
    blockn=str(blockn)
    for i in range(0,5-len(blockn)):
        blockn='0'+blockn
    blockn='blk'+blockn

    file_path=file_path+blockn+'.dat'

    file=open(file_path,'r')

    contents=file.read()
    return contents
