# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.

GECODE_VERSION = "5.1.0"
GATHER_STATS_URL = "http://user.it.uu.se/~pierref/courses/COCP/homeworks/gather_stats.py"
PYTHON_PACKAGES = "python3.6 python3-matplotlib python3-virtualenv python3-pip python3-tk"
GECODE_DEPS = "build-essential g++ libqt4-dev"
EXTRA_PACKAGES = "texlive-full language-pack-en"

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/zesty64"
  # Customize the amount of memory on the VM (only VirtualBox)
  config.vm.provider "virtualbox" do |vb|
    #vb.memory = "4096"
    vb.memory = "8192"
    vb.cpus = 8
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
  end

  # Install gecode,
  config.vm.provision "shell", inline: <<-SHELL
     apt-get update
     apt-get install -y #{GECODE_DEPS} #{PYTHON_PACKAGES} #{EXTRA_PACKAGES}
     wget --quiet http://www.gecode.org/download/gecode-#{GECODE_VERSION}.tar.gz
     tar xvf gecode-#{GECODE_VERSION}.tar.gz
     cd gecode-#{GECODE_VERSION} && ./configure --prefix=/usr/ --with-qt --disable-examples && make && make install
     wget --quiet --output-document=/usr/local/bin/gather_stats.py  #{GATHER_STATS_URL}
     chmod +x /usr/local/bin/gather_stats.py
  SHELL

  # For gist!
  config.ssh.forward_x11 = true
  config.ssh.forward_agent
end
