# David Park
# dappark
# 109582425

import sys
import time
import datetime
import dns.name
import dns.message
import dns.query

rootServers = (
    "198.41.0.4",
    "199.9.14.201",
    "192.33.4.12",
    "199.7.91.13",
    "192.203.230.10",
    "192.5.5.241",
    "192.112.36.4",
    "198.97.190.53",
    "192.36.148.17",
    "192.58.128.30",
    "193.0.14.129",
    "199.7.83.42",
    "202.12.27.33",
)


def queryTimeout():
    sys.exit("Domain not found/Response timed out")


def query(domain):
    # Create DNS query
    question = dns.message.make_query(domain, "A")
    # Send a request to root server
    answer = dns.query.udp(question, rootServers[0], 2)
    # Iterate through DNS until AA is reached
    while not answer.sections[1]:
        # If ADDITIONAL section is empty, query the domain of the nameserver
        if not answer.sections[3]:
            nameServer = dns.name.from_text(str(answer.sections[2][0][0]))
            # Make a recursive call to get the IP
            nameServerIP = query(nameServer)
            nameServerIP = str(nameServerIP.sections[1][0][0])
            answer = dns.query.udp(question, nameServerIP)
        # Else, use the IPv4 address in ADDITIONAL
        else:
            for x in answer.sections[3]:
                # Use IPv4 address
                if x.rdtype == 1:
                    answer = dns.query.udp(question, str(x[0]))
                    break
    # If CNAME is given, handle CDN redirection and query the CNAME
    if answer.sections[1][0].rdtype == 5:
        answer = query(dns.name.from_text(str(answer.sections[1][0][0])))
    return answer


# Take domain from command line as argument
domain = dns.name.from_text(sys.argv[1])

# Keep track of current time and start time
currentTime = datetime.datetime.now()
start = time.perf_counter()

# Query the domain
try:
    answer = query(domain)
except:
    queryTimeout()

answer = answer.sections[1][0]

end = time.perf_counter()

# Print formatted output
print("QUESTION SECTION:")
print(domain, "    IN      A\n")
print("ANSWER SECTION:")
for x in answer:
    print(domain, answer.ttl, " IN      A ", x)
print()
print("Query time: ", int((end - start) * 1000), "msec")
print("WHEN: ", currentTime.strftime("%m/%d/%Y %H:%M:%S"))
