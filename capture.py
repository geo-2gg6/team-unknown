import time
from typing import Any, Dict, List

try:
    from scapy.all import IP, TCP, sniff  # type: ignore
except Exception:  # scapy might be missing or unavailable on some systems
    IP = None  # type: ignore
    TCP = None  # type: ignore
    sniff = None  # type: ignore


def _packet_to_event(pkt: Any) -> Dict[str, Any]:
    ts = float(getattr(pkt, "time", time.time()))
    size = int(len(pkt)) if pkt is not None else 0
    dst_ip = None
    dst_port = None
    try:
        if IP and pkt.haslayer(IP):
            dst_ip = pkt[IP].dst
        if TCP and pkt.haslayer(TCP):
            dst_port = int(pkt[TCP].dport)
    except Exception:
        pass
    return {
        "dst_ip": dst_ip,
        "dst_port": dst_port,
        "size": size,
        "timestamp": ts,
    }


def capture_events(duration_seconds: int = 5) -> List[Dict[str, Any]]:
    """
    Capture outbound TCP packets to common web ports for a short window.

    Returns a list of small event dicts consumable by a Flask backend:
      { dst_ip, dst_port, size, timestamp }

    Notes:
    - Scapy sniffing generally requires root/admin privileges on Linux/macOS and
      Npcap/Admin on Windows. Without sufficient privileges, this will likely
      return an empty list.
    - Uses a BPF filter for efficiency: "ip and tcp and (dst port 80 or dst port 443)".
    """
    events: List[Dict[str, Any]] = []

    if sniff is None:
        return events

    bpf_filter = "ip and tcp and (dst port 80 or dst port 443)"

    try:
        # store=True collects packets for post-processing; timeout bounds capture duration
        packets = sniff(filter=bpf_filter, store=True, timeout=duration_seconds)
    except Exception:
        # Permission errors or missing backend (libpcap/Npcap) will land here
        return events

    for pkt in packets or []:
        try:
            events.append(_packet_to_event(pkt))
        except Exception:
            continue

    return events


if __name__ == "__main__":
    import json
    print(json.dumps(capture_events(), indent=2))


