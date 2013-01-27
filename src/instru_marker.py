'''
look for objc_msgsend dispatch function and trace every instruction
that influence the r0 and r1. then mark the information of this instruction
as a comment
'''

import idc, idaapi, idautils
import time
import logging

opertype = ['o_void', 'o_reg', 'o_mem', 'o_phrase', 'o_displ',
            'o_imm', 'o_far', 'o_near']
logger = logging.getLogger('lios.instruction')

def start_logger(logger):
    global logger
    logging

def trace_data(ea, min_ea, op_type, op_val):
    '''
    trace from ea to previous instruction, if the instruction is an
    effect(change the destination register) instruction. return the
    instruction. e.g:
    LDR R0, R3
    '''
    ea_call = ea
    while ea != idc.BADADDR and ea != min_ea:
        ea = idc.PrevHead(ea, min_ea)

        if op_type == idaapi.o_reg and op_val == 0 and idaapi.is_call_insn(ea):
            # BL/BLX that will modify the R0
            #
            return None

        operand = idc.GetMnem(ea)
        if operand in ['LDR', 'MOV']:
            src_op = 1
            dest_op = 0
        elif operand == 'STR':
            src_op = 0
            dest_op = 1
        else:
            continue

        #debug
        if ea == 0x9778a:
            print 'ea_call: %x' %ea_call
            print 'op_type: %d, op_val: %d' %(op_type, op_val)

        if idc.GetOpType(ea, dest_op) == op_type and idc.GetOperandValue(ea, dest_op) == op_val:
            mark_instruction(ea)
            op_type = idc.GetOpType(ea, src_op)
            op_val = idc.GetOperandValue(ea, src_op)

def mark_instruction(ea):
    ori_commt = idc.GetDisasm(ea)
    if '|' in ori_commt: # be handled by this python script before
        ori_commt = ori_commt.split('|')[-1]
    elif ';' in ori_commt:
        ori_commt = ori_commt.split(';')[-1]
    else:
        ori_commt = ''

    commt = '(%s, %s), (%s, %s) |%s' %(opertype[idc.GetOpType(ea, 0)], idc.GetOperandValue(ea, 0),
                                   opertype[idc.GetOpType(ea, 1)], idc.GetOperandValue(ea, 1), ori_commt)
    idc.MakeComm(ea, commt)

def main():
    msgsend = '_objc_msgSend'
    total = 0
    t = time.time()

    for xref in idautils.XrefsTo(idc.LocByName(msgsend), idaapi.XREF_ALL):
        total += 1
        ea_call = xref.frm
        func_start = idc.GetFunctionAttr(ea_call, idc.FUNCATTR_START)
        if not func_start or func_start == idc.BADADDR:
            continue
        ea = ea_call
        trace_data(ea, func_start, idc.o_reg, 0)
        trace_data(ea, func_start, idc.o_reg, 1)
    print '\nFinal stats:\n\t%d total calls' %total
    print '\tAnalysis took %.2f seconds' %(time.time() -t)


if __name__ == '__main__':
    main()