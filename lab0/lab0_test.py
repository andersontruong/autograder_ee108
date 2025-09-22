import logging
import cocotb
from cocotb.triggers import Timer
from cocotb.types import LogicArray

# ns
cocotb.simtime.time_precision = -9
# Input bitwidth
bitwidth = 4

async def select(dut, option=''):
    match option:
        case 'ZERO':
            dut.left_pushbutton.value = 0
            dut.right_pushbutton.value = 0
        case 'ADD':
            dut.left_pushbutton.value = 0
            dut.right_pushbutton.value = 1
        case 'AND':
            dut.left_pushbutton.value = 1
            dut.right_pushbutton.value = 0
        case _:
            dut.left_pushbutton.value = 1
            dut.right_pushbutton.value = 1

async def test_operation(dut, A, B, option, operation):
    A_val = LogicArray(f'{A:04b}')
    B_val = LogicArray(f'{B:04b}')
    dut.A.value = A_val
    dut.B.value = B_val

    await select(dut, option=option)
    await Timer(1.0, unit='ns')
    assert dut.out.value == LogicArray(f'{operation(A, B):0{bitwidth}b}'[-bitwidth:]), f'{option}'

@cocotb.test()
@cocotb.parametrize(
    A=list(range(pow(2, bitwidth))),
    B=list(range(pow(2, bitwidth)))
)
async def test_add(dut, A, B):
    add_op  = lambda A, B: A + B
    await test_operation(dut, A, B, 'DEFAULT', add_op)
    await test_operation(dut, A, B, 'ADD', add_op)
test_add.points = 1

@cocotb.test()
@cocotb.parametrize(
    A=list(range(pow(2, bitwidth))),
    B=list(range(pow(2, bitwidth)))
)
async def test_and(dut, A, B):
    and_op  = lambda A, B: A & B
    await test_operation(dut, A, B, 'AND', and_op)
test_and.points = 1

@cocotb.test()
@cocotb.parametrize(
    A=list(range(pow(2, bitwidth))),
    B=list(range(pow(2, bitwidth)))
)
async def test_zero(dut, A, B):
    zero_op = lambda A, B: 0
    await test_operation(dut, A, B, 'ZERO', zero_op)
test_zero.points = 1
