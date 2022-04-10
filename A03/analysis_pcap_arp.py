import sys
import dpkt

# Read in file from command line
f = open(sys.argv[1], "rb")
pcap = dpkt.pcap.Reader(f)

for timestamp, buf in pcap:

    eth = dpkt.ethernet.Ethernet(buf)

    if not isinstance(eth.data, dpkt.arp.ARP):
        continue

    arp = bytes(eth.data)
    (hardware_type, protocol_type, hardware_size, protocol_size, opcode) = (
        arp[0:2],
        arp[2:4],
        arp[4:5],
        arp[5:6],
        arp[6:8],
    )
    print("-" * 50)
    if (int.from_bytes(opcode,"big") == 1):
        print("ARP REQUEST:")
    elif (int.from_bytes(opcode,"big") == 2):
        print("ARP REPLY:")
    print("Hardware type:", int.from_bytes(hardware_type,"big"))
    print("Protocol type:", "0x" + "".join(format(x,"02x") for x in protocol_type))
    print("Hardware size:", int.from_bytes(hardware_size,"big"))
    print("Protocol type:", int.from_bytes(protocol_size,"big"))
    print("Sender MAC address:", ":".join(format(x, "02x") for x in arp[8:14]))
    print("Sender IP address:", ".".join(format(x, "d") for x in arp[14:18]))
    print("Target MAC address:", ":".join(format(x, "02x") for x in arp[18:24]))
    print("Target IP address:", ".".join(format(x, "d") for x in arp[24:28]))

f.close()
