## VM onboarding tool
Vm onboarding framework was developed in order to make OVA file import process to Openstack deployment possible with one button click and simple interface. The tool allows user import local vm infrastructure to the Openstack server. Onboarding tool is developed using Flask as backend and AngularJS as a Frontend technologies.


### Quick start 

#### Intagrate Horizon 

Copy intagration file to horizon directory:

    cp _50_onboarding.py .../horizon/openstack_dashboard/enabled/

Copy view foled:
     
    cp -rf onboarding/ .../horizon/openstack_dashboard/dashboards/

And restart apache2 service:
    
    service apache2 restart

#### Run ova onbaording service  

First of all before importing OVA file make sure that local virtual machine images contain cloud init package. 

All requirements for the tool are specified in the requirements.txt file. Before starting, it is strongly recommended to use virtual environment:

    virtualenv env 
    source env/bin/activate 

Requirements can be easily installed with pip tool

    pip install -r requirements.txt

To run service execute run.py file:
    
    python run.py

### Configuration file
Backend configuration is located in “app/__init__.py ” file.

* **app.config['UPLOAD_FOLDER']** - _location of the folder where all ova files should be stored. Default value: '/home/ubuntu/temp/'_
* **app.config['ALLOWED_FILES']** - _the list of file extensions allowed to upload. Default value: ['ova']_ 
* **app.config['CIDR']** - _subnetwork address for all external networks. Default value: '172.168.0.0/24'_
* **app.config['PUBLIC_NET']** - _the name of internal network where NAT ports should be connected. Default value: 'private'_

### <a href ="https://youtu.be/kicrMyQYJeI" target="_blank">DEMO</a>
