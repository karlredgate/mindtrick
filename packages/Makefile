
PWD := $(shell pwd)

.PHONY: default build clean

SPECS    = $(wildcard *.spec)
PACKAGES = $(patsubst %.spec,%,$(SPECS))
RPMS     = $(patsubst %,%.rpm,$(PACKAGES))

default: tools build

tools:
	rpm --query rpm-build
	rpm --query rpmdevtools

build: $(RPMS)

%.rpm: %.spec
	mkdir -p rpm/SOURCES rpm/BUILD rpm/RPMS rpm/BUILDROOT
	spectool --get-files --directory rpm/SOURCES/ $^
	rpmbuild --quiet -bb --buildroot=$(PWD)/rpm/BUILDROOT $^
	mv rpm/RPMS/*/$(patsubst %.rpm,%,$@)*.rpm $@

# To rename the rpm to its correct name use:
# fullname=$( rpm --query --package $rpm ).rpm
# mv $rpm $fullname

clean:
	rm -f *.rpm
	rm -rf rpm
