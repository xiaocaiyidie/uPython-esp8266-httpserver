######################################################################
# User configuration
######################################################################
# Path to uploader 
UPLOADER=/opt/ESP8266/webrepl/webrepl_cli.py
ESPTOOL=/opt/ESP8266/esp-open-sdk/esptool/esptool.py
ESPSEND=/usr/local/bin/espsend.py
MPYCROSS=/opt/ESP8266/micropython/mpy-cross/mpy-cross

DATE=$(shell date +"%d %b %Y")

# Serial port
#PORT=/dev/cu.SLAB_USBtoUART
PORT=/dev/ttyUSB0
SPEED=115200

DEV=192.168.1.144
DEV=192.168.1.121
DEV=192.168.1.51
DEV=192.168.1.153

######################################################################
# End of user config
######################################################################
FILES := \
	main.py \
	ds18b20.py \
	request.py \
	content.py \
	config.py \
	httpserver.py \
	register.py \

TEXT:= \
	help.txt \
	header.txt \
	footer.txt \
	index.txt \

MPYFILES := \
	main.mpy \
	ds18b20.mpy \
	request.mpy \
	content.mpy \
	config.mpy \
	httpserver.mpy \
	register.mpy \

%.mpy: %.py
	$(MPYCROSS) $<

default: 
	@echo 'picocom -b 115200'
	@echo 'import webrepl; webrepl.start()'

check: $(MPYCROSS)
	python3 -m py_compile *.py
	rm -rf __pycache__
	rm -f *.pyc

all: $(MPYFILES)
	$(ESPSEND) -p $(PORT) -c -w
	for f in $^ ; \
	do \
		$(UPLOADER) $$f $(DEV):/$$f ;\
	done;

vi:
	gvim $(FILES)

# To flash firmware
flash:
	export PATH="/opt/ESP8266/esp-open-sdk/xtensa-lx106-elf/bin/:$$PATH" ;\
	$(ESPTOOL) --port $(PORT) erase_flash ;\
	cd /opt/ESP8266/micropython/esp8266 ;\
	make PORT=$(PORT) deploy

initmicro:
	$(ESPSEND) -p $(PORT) -c 
	$(ESPSEND) -p $(PORT) --file net.py --target main.py
	$(ESPSEND) -p $(PORT) -r 

# Upload all
allshell: $(MPYFILES) check
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	@python espsend.py -c -w
	for f in $(MPYFILES); \
	do \
		$(UPLOADER) $$f $(DEV):/$$f ;\
	done; \
	for f in $(TEXT); \
	do \
		$(UPLOADER) $$f $(DEV):/$$f ;\
	done;
	@python espsend.py -r

m: main.py 
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	$(ESPSEND) -p $(PORT) -c -w
	$(UPLOADER) $^ $(DEV):/$^
f: config.mpy 
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	$(ESPSEND) -p $(PORT) -c -w
	$(UPLOADER) $^ $(DEV):/$^
d: ds18b20.mpy 
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	$(ESPSEND) -p $(PORT) -c -w
	$(UPLOADER) $^ $(DEV):/$^
g: register.mpy 
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	$(ESPSEND) -p $(PORT) -c -w
	$(UPLOADER) $^ $(DEV):/$^
h: httpserver.mpy 
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	$(ESPSEND) -p $(PORT) -c -w
	$(UPLOADER) $^ $(DEV):/$^
c: content.mpy 
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	$(ESPSEND) -p $(PORT) -c -w
	$(UPLOADER) $^ $(DEV):/$^
q: request.mpy 
	$(ESPSEND) -p $(PORT) -c -w
	$(UPLOADER) $^ $(DEV):/$^
hf: header.txt footer.txt
	$(ESPSEND) -p $(PORT) -c -w
	$(UPLOADER) $^ $(DEV):/$^

r:  
	$(ESPSEND) -p $(PORT) -c -r

reset:  check
	$(ESPSEND) -p $(PORT) -c -r


webrepl:
	/opt/google/chrome/chrome file:///opt/ESP8266/webrepl/webrepl.html

git:
	git commit -m 'update ${DATE}' -a
	git push

clean:
	rm -f *.pyc

# Print usage
usage:
	@echo "make upload FILE=<file>  to upload a specific file (i.e make upload FILE:=request.py)"
	@echo "make all           		to upload all"
	@echo "make <x>                 where <x> is the initial of source file "

