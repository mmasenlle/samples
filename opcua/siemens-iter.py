import sys
sys.path.insert(0, "..")


from opcua import Client
from opcua import ua


if __name__ == "__main__":

    # client = Client("opc.tcp://localhost:4840/freeopcua/server/")
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
    
    client = Client("opc.tcp://172.24.0.100:4840")
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        #print("Objects node is: ", root)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        #print("Children of root are: ", root.get_children())

        plcvars = client.get_node('ns=3;s=Memory')
        for var in plcvars.get_children():
            if var.get_browse_name().Name == 'Icon': continue
            print(var.get_browse_name().Name,':',var.get_value())
        plcdbs = client.get_node('ns=3;s=DataBlocksGlobal')
        for db in plcdbs.get_children():
            if db.get_browse_name().Name == 'Icon': continue
            if db.get_browse_name().Name.startswith('IEC_'): continue
            for var in db.get_children():
                if var.get_browse_name().Name == 'Icon': continue
                print('{}.{}: {}'.format(db.get_browse_name().Name,var.get_browse_name().Name,var.get_value()))
        plcdbins = client.get_node('ns=3;s=DataBlocksInstance')
        for db in plcdbins.get_children():
            if db.get_browse_name().Name == 'Icon': continue
            if db.get_browse_name().Name.startswith('IEC_'): continue
            for obj in db.get_children():
                for var in obj.get_children():
                    if var.get_browse_name().Name == 'Icon': continue
                    print('{}.{}: {}'.format(db.get_browse_name().Name,var.get_browse_name().Name,var.get_value()))
                            
        # get a specific node knowing its node id
        #var = client.get_node(ua.NodeId(1002, 2))
        #var = client.get_node("ns=3;i=2002")
        #print(var)
        #var.get_data_value() # get value of node as a DataValue object
        #var.get_value() # get value of node as a python builtin
        #var.set_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
        #var.set_value(3.9) # set node value using implicit data type

        # Now getting a variable node using its browse path
        # myvar = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable"])
        # bombilla = root.get_child(["0:Objects", "3:PLC_PruebaOPC", "3:Memory", "3:bombilla"])
        # boton = root.get_child(["0:Objects", "3:PLC_PruebaOPC", "3:Memory", "3:boton"])
        # #obj = root.get_child(["0:Objects", "2:MyObject"])
        
        # while True:
            # print("bombilla: ", bombilla.get_value())
            # print("boton: ", boton.get_value())
            # c = sys.stdin.read(1)
            # if c == 'q': break
            # if c == '1': boton.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
            # if c == '0': boton.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))) #(.set_value(False)
        # #print("myobj is: ", obj)

        # Stacked myvar access
        #print("myvar is: ", root.get_children()[0].get_children()[1].get_variables()[0].get_value())

    finally:
        client.disconnect()
