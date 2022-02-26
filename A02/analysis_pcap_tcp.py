import sys
import datetime
import dpkt
from dpkt.utils import *

# Read in file from command line
f = open(sys.argv[1], "rb")
pcap = dpkt.pcap.Reader(f)

srcIP = None
dstIP = None
outFlow = {}
inFlow = {}
packets = {}
outTransactions = {}
inTransactions = {}
outTime = {}
inTime = {}
outWindow = {}
inWindow = {}
throughput = {}
startTime = {}
endTime = {}
totalTime = {}
window = {}

# For each packet in the pcap process the contents
for timestamp, buf in pcap:

    # Unpack the Ethernet frame (mac src/dst, ethertype)
    eth = dpkt.ethernet.Ethernet(buf)

    # Make sure the Ethernet data contains an IP packet
    if not isinstance(eth.data, dpkt.ip.IP):
        continue

    # Now grab the data within the Ethernet frame (the IP packet)
    ip = eth.data
    # Store src and dst IP (as string)
    if not srcIP:
        srcIP = inet_to_str(ip.src)
    if not dstIP:
        dstIP = inet_to_str(ip.dst)

    # Check for TCP in the transport layer
    if isinstance(ip.data, dpkt.tcp.TCP):
        # Set the TCP data
        tcp = ip.data

        # snd -> rcv
        if inet_to_str(ip.src) == srcIP:
            # srcPort -> dstPort
            if tcp.sport not in outFlow:
                outFlow[tcp.sport] = tcp.dport
                window[tcp.sport] = tcp.win
                packets[tcp.sport] = 0
                throughput[tcp.sport] = 0
                startTime[tcp.sport] = datetime.datetime.utcfromtimestamp(timestamp)
            packets[tcp.sport] += 1
            throughput[tcp.sport] += len(tcp.data)
            # Store the first 2 outbound packets after the handshake
            if tcp.flags == 24 and tcp.sport not in outTransactions.keys():
                outTransactions[tcp.sport] = []
                outTransactions[tcp.sport].append(tcp)
                outTime[tcp.sport] = []
                outTime[tcp.sport].append(str(datetime.datetime.utcfromtimestamp(timestamp)))
                outWindow[tcp.sport] = []
                outWindow[tcp.sport].append(tcp.win)
            elif tcp.sport in outTransactions.keys():
                if len(outTransactions[tcp.sport]) < 2:
                    if tcp.flags == 16:
                        outTransactions[tcp.sport].append(tcp)
                        outTime[tcp.sport].append(str(datetime.datetime.utcfromtimestamp(timestamp)))
                        outWindow[tcp.sport].append(tcp.win)
        # rcv -> snd
        if inet_to_str(ip.src) == dstIP:
            # dstPort -> sndPort
            if tcp.dport not in inFlow:
                inFlow[tcp.dport] = tcp.sport
            packets[tcp.dport] += 1
            # Store the first 2 inbound packets after the handshake
            if tcp.flags == 16 and tcp.dport not in inTransactions.keys():
                inTransactions[tcp.dport] = []
                inTransactions[tcp.dport].append(tcp)
                inTime[tcp.dport] = []
                inTime[tcp.dport].append(str(datetime.datetime.utcfromtimestamp(timestamp)))
                inWindow[tcp.dport] = []
                inWindow[tcp.dport].append(tcp.win)
            elif tcp.dport in inTransactions.keys():
                if len(inTransactions[tcp.dport]) < 2:
                    if tcp.flags == 16:
                        inTransactions[tcp.dport].append(tcp)
                        inTime[tcp.dport].append(str(datetime.datetime.utcfromtimestamp(timestamp)))
                        inWindow[tcp.dport].append(tcp.win)
        if tcp.flags == 17:
            endTime[tcp.dport] = datetime.datetime.utcfromtimestamp(timestamp)
            totalTime[tcp.dport] = (endTime[tcp.dport] - startTime[tcp.dport]).total_seconds()

print("TOTAL FLOWS:", len(outFlow))
index = 1
for srcPort in outFlow:
    print("Flow #%d" % index)
    print("SRC IP: %s" % srcIP)
    print("PORT  :", srcPort)
    print("DST IP: %s" % dstIP)
    print("PORT  :", outFlow[srcPort])
    print("Window:", window[srcPort])
    print("\nTotal Packets:", packets[srcPort])
    print("Throughput: %d (bytes/sec)" % ((throughput[srcPort]/8)/totalTime[srcPort]))
    print("\nFlow #%d Transactions" % index)
    print(
        f"type\t\tflag\t\tseq\t\tack\t\twindow\t\ttime\n"
        f"snd -> rev\tPUSH,ACK\t{outTransactions[srcPort][0].seq}\t{outTransactions[srcPort][0].ack}\t{outWindow[srcPort][0]}\t\t{outTime[srcPort][0]}\n"
        f"rev -> snd\tACK\t\t{inTransactions[srcPort][0].seq}\t{inTransactions[srcPort][0].ack}\t{inWindow[srcPort][0]}\t\t{inTime[srcPort][0]}\n"
        f"snd -> rev\tACK\t\t{outTransactions[srcPort][1].seq}\t{outTransactions[srcPort][1].ack}\t{outWindow[srcPort][1]}\t\t{outTime[srcPort][1]}\n"
        f"rev -> snd\tACK\t\t{inTransactions[srcPort][1].seq}\t{inTransactions[srcPort][1].ack}\t{inWindow[srcPort][1]}\t\t{inTime[srcPort][1]}\n"
    )


    print("\n")
    index += 1

f.close()
