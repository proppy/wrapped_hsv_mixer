PWDD := $(shell pwd)
BLOCKS := $(shell basename $(PWDD))

# ---- Include Partitioned Makefiles ----

CONFIG = caravel_user_project

export COCOTB_REDUCED_LOG_FMT=1
export PYTHONPATH := $(DESIGNS)/verilog/rtl/wrapped_hsv_mixer/hsv_mixer/test
export LIBPYTHON_LOC=$(shell cocotb-config --libpython)


include $(MCW_ROOT)/verilog/dv/make/env.makefile
include $(MCW_ROOT)/verilog/dv/make/var.makefile
include $(MCW_ROOT)/verilog/dv/make/cpu.makefile
include $(MCW_ROOT)/verilog/dv/make/sim.makefile

coco_test: hsv_mixer.hex
	rm -rf sim_build/
	mkdir sim_build/

	iverilog -Ttyp -DFUNCTIONAL -DSIM -DUSE_POWER_PINS -DUNIT_DELAY=#1 \
	-f$(VERILOG_PATH)/includes/includes.rtl.caravel \
	-f$(USER_PROJECT_VERILOG)/includes/includes.rtl.$(CONFIG) -o sim_build/sim.vvp hsv_mixer_tb.v

	TESTCASE=test_start,test_all MODULE=test_hsv_mixer vvp -M $$(cocotb-config --prefix)/cocotb/libs -m libcocotbvpi_icarus sim_build/sim.vvp
	! grep failure results.xml

coco_test_gl: hsv_mixer.hex
	rm -rf sim_build/
	mkdir sim_build/

	iverilog -Ttyp -DFUNCTIONAL -DSIM -DUSE_POWER_PINS -DUNIT_DELAY=#1 \
	-f$(VERILOG_PATH)/includes/includes.rtl.caravel \
	-f$(USER_PROJECT_VERILOG)/includes/includes.gl.$(CONFIG) -o sim_build/sim.vvp hsv_mixer_tb.v

	TESTCASE=test_start,test_all_gl MODULE=test_hsv_mixer vvp -M $$(cocotb-config --prefix)/cocotb/libs -m libcocotbvpi_icarus sim_build/sim.vvp
	! grep failure results.xml
