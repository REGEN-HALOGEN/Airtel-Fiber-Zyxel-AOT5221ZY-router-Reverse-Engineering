import xml.etree.ElementTree as ET

tree = ET.parse('files/aot-current-pdm-config.xml')
root = tree.getroot()

wan_conn_dev = root.find('.//WANConnectionDevice')
if wan_conn_dev is not None:
    for child in wan_conn_dev:
        print(f"Instance tag: {child.tag}")
        for sub in child:
            print(f"  Sub-object: {sub.tag}")
            for sub_inst in sub:
                print(f"    Sub-instance: {sub_inst.tag}")
                for param in sub_inst:
                    if param.tag in ['Name', 'Enable', 'ConnectionType', 'X_5067F0_InterfaceName', 'X_5067F0_IfName', 'Username', 'PPPoEServiceName', 'MaxMRUSize', 'X_5067F0_MaxMTUSize', 'X_5067F0_PPPAuthenticationProtocol', 'NATEnabled', 'X_5067F0_Enable_VLANID', 'X_5067F0_VLANID']:
                        print(f"      {param.tag} = {param.text}")

