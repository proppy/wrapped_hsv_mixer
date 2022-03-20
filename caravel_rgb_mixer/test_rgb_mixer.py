import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, with_timeout
import random
from test_encoder import Encoder

clocks_per_phase = 10

# takes ~60 seconds on my PC
@cocotb.test()
async def test_start(dut):
    clock = Clock(dut.clk, 25, units="ns")
    cocotb.fork(clock.start())
    
    dut.RSTB.value = 0
    dut.power1.value = 0;
    dut.power2.value = 0;
    dut.power3.value = 0;
    dut.power4.value = 0;

    await ClockCycles(dut.clk, 8)
    dut.power1.value = 1;
    await ClockCycles(dut.clk, 8)
    dut.power2.value = 1;
    await ClockCycles(dut.clk, 8)
    dut.power3.value = 1;
    await ClockCycles(dut.clk, 8)
    dut.power4.value = 1;

    await ClockCycles(dut.clk, 80)
    dut.RSTB.value = 1

    # wait for the project to become active
    await with_timeout(RisingEdge(dut.uut.mprj.wrapped_rgb_mixer_3.active), 500, 'us')

async def run_encoder_test(encoder, dut_enc, max_count):
    for i in range(clocks_per_phase * 2 * max_count):
        await encoder.update(1)

    # let noisy transition finish, otherwise can get an extra count
    for i in range(10):
        await encoder.update(0)
    
    # when we have the internal signals (not GL) can also assert the values
    if dut_enc is not None:
        assert(dut_enc == max_count)

@cocotb.test()
async def test_all(dut):
    clock = Clock(dut.clk, 25, units="ns")

    encoder0 = Encoder(dut.clk, dut.enc0_a, dut.enc0_b, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)
    encoder1 = Encoder(dut.clk, dut.enc1_a, dut.enc1_b, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)
    encoder2 = Encoder(dut.clk, dut.enc2_a, dut.enc2_b, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)

    cocotb.fork(clock.start())

    # wait for the reset signal - time out if necessary - should happen around 165us
    await with_timeout(RisingEdge(dut.uut.mprj.wrapped_rgb_mixer_3.rgb_mixer0.reset), 500, 'us')
    await FallingEdge(dut.uut.mprj.wrapped_rgb_mixer_3.rgb_mixer0.reset)

    assert dut.uut.mprj.wrapped_rgb_mixer_3.rgb_mixer0.enc0.value == 0
    assert dut.uut.mprj.wrapped_rgb_mixer_3.rgb_mixer0.enc1.value == 0
    assert dut.uut.mprj.wrapped_rgb_mixer_3.rgb_mixer0.enc2.value == 0

    # pwm should all be low at start
    assert dut.pwm0_out.value == 0
    assert dut.pwm1_out.value == 0
    assert dut.pwm1_out.value == 0

    max_ramp = 255
    # ramp val
    await run_encoder_test(encoder2, dut.enc2, max_ramp)
    assert dut.rgb == 0xffffff
    await RisingEdge(dut.pwm0_out)
    for i in range(255):
        assert dut.pwm0_out == 1
        assert dut.pwm1_out == 1
        assert dut.pwm2_out == 1
        await ClockCycles(dut.clk, 1)

    # ramp sat up
    await run_encoder_test(encoder1, dut.enc1, max_ramp)

    assert dut.rgb == 0xff0000
    await RisingEdge(dut.pwm0_out)
    for i in range(255):
        assert dut.pwm0_out == 1
        assert dut.pwm1_out == 0
        assert dut.pwm2_out == 0
        await ClockCycles(dut.clk, 1)

    # ramp hue
    await run_encoder_test(encoder0, dut.enc0, max_ramp+1)
    assert dut.rgb == 0xffff00
    await RisingEdge(dut.pwm0_out)
    for i in range(255):
        assert dut.pwm0_out == 1
        assert dut.pwm1_out == 1
        assert dut.pwm2_out == 0
        await ClockCycles(dut.clk, 1)

@cocotb.test()
async def test_all_gl(dut):
    clock = Clock(dut.clk, 25, units="ns")

    encoder0 = Encoder(dut.clk, dut.enc0_a, dut.enc0_b, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)
    encoder1 = Encoder(dut.clk, dut.enc1_a, dut.enc1_b, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)
    encoder2 = Encoder(dut.clk, dut.enc2_a, dut.enc2_b, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)

    cocotb.fork(clock.start())

    # wait for the reset signal - time out if necessary - should happen around 165us
    await with_timeout(RisingEdge(dut.design_reset), 180, 'us')
    await FallingEdge(dut.design_reset)
    print("design reset ok")

    # pwm should all be low at start
    assert dut.pwm0_out.value == 0
    assert dut.pwm1_out.value == 0
    assert dut.pwm1_out.value == 0
    print("pwm all 0")

    max_ramp = 255
    # ramp val
    await run_encoder_test(encoder2, dut.enc2, max_ramp)
    assert dut.rgb == 0xffffff
    await RisingEdge(dut.pwm0_out)
    for i in range(255):
        assert dut.pwm0_out == 1
        assert dut.pwm1_out == 1
        assert dut.pwm2_out == 1
        await ClockCycles(dut.clk, 1)

    # ramp sat up
    await run_encoder_test(encoder1, dut.enc1, max_ramp)

    assert dut.rgb == 0xff0000
    await RisingEdge(dut.pwm0_out)
    for i in range(255):
        assert dut.pwm0_out == 1
        assert dut.pwm1_out == 0
        assert dut.pwm2_out == 0
        await ClockCycles(dut.clk, 1)

    # ramp hue
    await run_encoder_test(encoder0, dut.enc0, max_ramp+1)
    assert dut.rgb == 0xffff00
    await RisingEdge(dut.pwm0_out)
    for i in range(255):
        assert dut.pwm0_out == 1
        assert dut.pwm1_out == 1
        assert dut.pwm2_out == 0
        await ClockCycles(dut.clk, 1)
