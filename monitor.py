import time
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import psutil
    from psutil import AccessDenied, NoSuchProcess
except Exception:  # psutil may be absent in some environments
    psutil = None  # type: ignore
    AccessDenied = Exception  # type: ignore
    NoSuchProcess = Exception  # type: ignore


ConnectionRecord = Dict[str, Any]


def _format_addr(addr: Optional[Tuple[str, int]]) -> Optional[str]:
    if not addr:
        return None
    host, port = addr
    return f"{host}:{port}"


def _get_process_name(pid: Optional[int], cache: Dict[int, str]) -> Optional[str]:
    if pid is None or not psutil:
        return None
    if pid in cache:
        return cache[pid]
    try:
        name = psutil.Process(pid).name()
        if name:
            cache[pid] = name
        return name
    except (NoSuchProcess, AccessDenied, ProcessLookupError):
        return None
    except Exception:
        return None


def _is_outgoing_established(status: str, raddr: Optional[Tuple[str, int]]) -> bool:
    if not raddr:
        return False
    return status.upper() in {"ESTABLISHED", "CONNECTED"}


def _unique_conn_key(conn: "psutil._common.sconn") -> Tuple:
    return (
        getattr(conn, "pid", None),
        getattr(conn, "laddr", None),
        getattr(conn, "raddr", None),
        getattr(conn, "status", None),
    )


def _collect_tcp_connections_primary() -> List["psutil._common.sconn"]:
    if not psutil:
        return []
    try:
        return psutil.net_connections(kind="tcp")
    except AccessDenied:
        return []
    except Exception:
        return []


def _collect_tcp_connections_fallback_current_user() -> List["psutil._common.sconn"]:
    results: List["psutil._common.sconn"] = []
    if not psutil:
        return results
    try:
        current_user = psutil.Process().username()
    except Exception:
        current_user = None
    try:
        for proc in psutil.process_iter(attrs=["pid", "username"]):
            try:
                if current_user and proc.info.get("username") != current_user:
                    continue
                conns = proc.connections(kind="tcp")
                results.extend(conns)
            except (AccessDenied, NoSuchProcess):
                continue
            except Exception:
                continue
    except Exception:
        return results
    return results


def _collect_tcp_connections() -> List["psutil._common.sconn"]:
    conns = _collect_tcp_connections_primary()
    if conns:
        return conns
    return _collect_tcp_connections_fallback_current_user()


def sample_connections() -> List[ConnectionRecord]:
    """
    Return a list of dicts for outgoing TCP connections that are ESTABLISHED/CONNECTED.

    Dict schema: { pid, process_name, laddr, raddr, status, timestamp }
    """
    now = time.time()
    records: List[ConnectionRecord] = []
    if not psutil:
        return records

    name_cache: Dict[int, str] = {}
    seen: Set[Tuple] = set()

    for conn in _collect_tcp_connections():
        try:
            status = getattr(conn, "status", "")
            raddr = getattr(conn, "raddr", None)
            if not _is_outgoing_established(status, raddr):
                continue

            key = _unique_conn_key(conn)
            if key in seen:
                continue
            seen.add(key)

            pid = getattr(conn, "pid", None)
            process_name = _get_process_name(pid, name_cache)
            laddr = _format_addr(getattr(conn, "laddr", None))
            raddr_str = _format_addr(raddr)

            records.append(
                {
                    "pid": pid,
                    "process_name": process_name,
                    "laddr": laddr,
                    "raddr": raddr_str,
                    "status": status,
                    "timestamp": now,
                }
            )
        except Exception:
            continue

    return records


if __name__ == "__main__":
    import json
    try:
        print(json.dumps(sample_connections(), indent=2))
    except Exception as e:
        print(f"Error sampling connections: {e}")


