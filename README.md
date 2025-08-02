#XIQ-SE SDK Python

ExtremeCloudIQ Site Engine SDK Python

## Installation & Usage

```bash
git clone https://github.com/tchevalleraud/XIQSE-SDK-Python.git /tmp/xiqse_tmp && \
cp -r /tmp/xiqse_tmp/XIQSE /usr/local/Extreme_Networks/NetSight/jython/Lib/ && \
rm -rf /tmp/xiqse_tmp
```

### pip install (OLD)

#### Prepare ExtremeCloudIQ Site Engine

```bash
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py
python2.7 get-pip.py
```

#### Install Python package

```bash
python2.7 -m pip install git+https://github.com/tchevalleraud/XIQSE-SDK-Python.git
```

#### Upgrade Python package

```bash
python2.7 -m pip install --upgrade --no-cache-dir git+https://github.com/tchevalleraud/XIQSE-SDK-Python.git
```

#### Python pip list

```bash
python2.7 -m pip list
```

#### Uninstall Python package 

```bash
python2.7 -m pip uninstall XIQSE
```